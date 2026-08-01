<##
.SYNOPSIS
Runs bounded, resumable Codex audits for the six study-package layers.

.DESCRIPTION
Creates one input, stdout log, stderr log, and result record per layer. It
uses direct stream copies instead of Out-String. Codex CLI status normally
arrives on stderr while the final audit arrives on stdout, so both streams are
preserved and file sizes are printed during long-running work.

Run -DryRun first. Select an explicit isolated authentication backend rather
than relying on whichever account a parent terminal happened to load.
#>
[CmdletBinding()]
param(
    [ValidateSet(
        '01_应用层',
        '02_运输层',
        '03_网络层',
        '04_数据链路层',
        '05_物理层',
        '06_网络安全'
    )]
    [string[]]$Layer = @(
        '01_应用层',
        '02_运输层',
        '03_网络层',
        '04_数据链路层',
        '05_物理层',
        '06_网络安全'
    ),

    [ValidateRange(1, 6)]
    [int]$ThrottleLimit = 2,

    [ValidateRange(5, 120)]
    [int]$TimeoutMinutes = 30,

    [string]$Model = 'gpt-5.6-sol',

    # `juanji-api` matches this machine's `codex-api` terminal entry.  Use
    # `openai-api` for the independently stored OpenAI Platform credential.
    [ValidateSet('juanji-api', 'openai-api', 'plus', 'direct')]
    [string]$AuthBackend = 'juanji-api',

    # Optional PowerShell launcher. It is useful for an alternate isolated
    # backend and is invoked through pwsh -NoProfile -File.
    [string]$LauncherPath,

    # Optional override for an executable compatible with `codex exec ...`.
    # It allows the runner itself to be exercised with a local mock command.
    [string]$CodexPath,

    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$repoRoot = Split-Path -Parent $PSScriptRoot
$packageRoot = Join-Path $repoRoot '07_考研预备_分层学习包'
$runId = Get-Date -Format 'yyyyMMdd-HHmmssfff'
$runRoot = Join-Path $repoRoot ("analysis\codex-audit\{0}" -f $runId)
while (Test-Path -LiteralPath $runRoot) {
    Start-Sleep -Milliseconds 1
    $runId = Get-Date -Format 'yyyyMMdd-HHmmssfff'
    $runRoot = Join-Path $repoRoot ("analysis\codex-audit\{0}" -f $runId)
}
New-Item -ItemType Directory -Path $runRoot -Force | Out-Null

$prefixesByLayer = @{
    '01_应用层' = @('01_', '04_', '05_', '06_', '07_')
    '02_运输层' = @('01_', '04_', '05_', '06_', '07_')
    '03_网络层' = @('01_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')
    '04_数据链路层' = @('01_', '04_', '05_', '06_', '07_')
    '05_物理层' = @('01_', '04_', '05_', '06_', '07_')
    '06_网络安全' = @('01_', '04_', '05_', '06_', '07_')
}

function Get-AuditFiles {
    param([string]$LayerName)

    $layerPath = Join-Path $packageRoot $LayerName
    if (-not (Test-Path -LiteralPath $layerPath -PathType Container)) {
        throw "Layer directory does not exist: $layerPath"
    }

    $prefixes = $prefixesByLayer[$LayerName]
    Get-ChildItem -LiteralPath $layerPath -File -Filter '*.md' |
        Where-Object {
            $name = $_.Name
            $prefixes | Where-Object { $name.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }
        } |
        Sort-Object Name
}

function New-LayerInput {
    param(
        [string]$LayerName,
        [System.IO.FileInfo[]]$Files,
        [string]$InputPath
    )

    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.AppendLine("# 审核输入：$LayerName")
    [void]$builder.AppendLine('')
    foreach ($file in $Files) {
        $relative = $file.FullName.Substring($repoRoot.Length).TrimStart('\', '/')
        [void]$builder.AppendLine("## 文件：$relative")
        [void]$builder.AppendLine('```markdown')
        [void]$builder.AppendLine([System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8))
        [void]$builder.AppendLine('```')
        [void]$builder.AppendLine('')
    }

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($InputPath, $builder.ToString(), $utf8NoBom)
}

function Get-AuditPrompt {
    param([string]$LayerName)

    @"
你是 408 计算机网络资料的独立验收员。审核对象是 $LayerName，资料正文通过标准输入提供。

逐文件检查：
1. 知识点正确性：事实错误、公式/计算错误、互相矛盾的表述。
2. 408 考纲覆盖：遗漏的核心考点。
3. 真题答案一致性：只在资料明确标注“试卷 X 第 Y 题”且可在 D:\计算机网络试卷\converted_utf8\计算机网络试卷_X.md 找到同题号答案时核对；没有明确映射时必须写“未建立映射”，不得把相似题目当作同一道题。
4. 结构完整性：零基础版、题型训练、错题本、默写、速查之间的缺口或冲突。

输出格式：
## 文件: [文件名]
- [严重] 问题描述
- [一般] 问题描述
- [建议] 问题描述

最后给 $LayerName 总评分（0-100）和一句结论。请引用准确的文件名和可定位的原文片段；没有问题的项目写“未发现”。
"@
}

function Resolve-CodexCommand {
    param(
        [string]$Backend,
        [string]$CustomLauncherPath,
        [string]$ExecutablePath
    )

    if (-not [string]::IsNullOrWhiteSpace($CustomLauncherPath) -and -not [string]::IsNullOrWhiteSpace($ExecutablePath)) {
        throw 'Specify either -LauncherPath or -CodexPath, not both.'
    }

    if (-not [string]::IsNullOrWhiteSpace($ExecutablePath)) {
        $resolvedExecutable = (Resolve-Path -LiteralPath $ExecutablePath -ErrorAction Stop).Path
        return [pscustomobject]@{
            FileName = $resolvedExecutable
            PrefixArguments = @()
            Description = $resolvedExecutable
        }
    }

    if ([string]::IsNullOrWhiteSpace($CustomLauncherPath) -and $Backend -eq 'direct') {
        $directCommand = Get-Command 'codex.cmd' -ErrorAction SilentlyContinue
        if ($null -eq $directCommand) {
            $directCommand = Get-Command 'codex' -ErrorAction Stop
        }
        return [pscustomobject]@{
            FileName = $directCommand.Source
            PrefixArguments = @()
            Description = "direct: $($directCommand.Source)"
        }
    }

    if ([string]::IsNullOrWhiteSpace($CustomLauncherPath)) {
        $launcherNames = @{
            'juanji-api' = 'codex-juanji.ps1'
            'openai-api' = 'codex-api.ps1'
            'plus' = 'codex-plus.ps1'
        }
        $CustomLauncherPath = Join-Path $env:USERPROFILE (Join-Path 'codex-launchers' $launcherNames[$Backend])
    }

    $resolvedLauncher = (Resolve-Path -LiteralPath $CustomLauncherPath -ErrorAction Stop).Path
    $powerShell = Get-Command 'pwsh' -ErrorAction SilentlyContinue
    if ($null -eq $powerShell) {
        $powerShell = Get-Command 'powershell' -ErrorAction Stop
    }
    return [pscustomobject]@{
        FileName = $powerShell.Source
        PrefixArguments = @('-NoLogo', '-NoProfile', '-File', $resolvedLauncher)
        Description = "$Backend launcher: $resolvedLauncher"
    }
}

function Start-CodexAudit {
    param(
        [pscustomobject]$CodexCommand,
        [string]$LayerName,
        [string]$InputPath,
        [string]$StdoutPath,
        [string]$StderrPath
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $CodexCommand.FileName
    $startInfo.WorkingDirectory = $repoRoot
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    # Codex expects piped prompts in UTF-8. Without this, Windows PowerShell
    # writes Chinese study material using the active code page.
    $startInfo.StandardInputEncoding = [System.Text.UTF8Encoding]::new($false)
    foreach ($prefixArgument in $CodexCommand.PrefixArguments) {
        [void]$startInfo.ArgumentList.Add($prefixArgument)
    }
    $startInfo.ArgumentList.Add('exec')
    $startInfo.ArgumentList.Add('-m')
    $startInfo.ArgumentList.Add($Model)
    $startInfo.ArgumentList.Add('--skip-git-repo-check')
    $startInfo.ArgumentList.Add((Get-AuditPrompt -LayerName $LayerName))

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "Failed to start Codex for $LayerName"
    }

    $stdoutStream = [System.IO.File]::Open($StdoutPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    $stderrStream = [System.IO.File]::Open($StderrPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    # Begin draining both pipes before sending the full input.  This prevents a
    # verbose child process from filling an output pipe while stdin is written.
    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutStream)
    $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrStream)
    $input = [System.IO.File]::ReadAllText($InputPath, [System.Text.Encoding]::UTF8)
    $process.StandardInput.Write($input)
    $process.StandardInput.Close()

    [pscustomobject]@{
        Layer = $LayerName
        Process = $process
        StartedAt = Get-Date
        TimedOut = $false
        StdoutStream = $stdoutStream
        StderrStream = $stderrStream
        StdoutTask = $stdoutTask
        StderrTask = $stderrTask
        StdoutPath = $StdoutPath
        StderrPath = $StderrPath
    }
}

function Complete-CodexAudit {
    param([pscustomobject]$Run)

    [void]$Run.StdoutTask.GetAwaiter().GetResult()
    [void]$Run.StderrTask.GetAwaiter().GetResult()
    [void]$Run.StdoutStream.Dispose()
    [void]$Run.StderrStream.Dispose()
    [void]$Run.Process.Refresh()
    $finishedAt = Get-Date

    [pscustomobject]@{
        Layer = $Run.Layer
        StartedAt = $Run.StartedAt
        FinishedAt = $finishedAt
        ExitCode = if ($Run.TimedOut) { 124 } else { $Run.Process.ExitCode }
        Status = if ($Run.TimedOut) { 'timeout' } elseif ($Run.Process.ExitCode -eq 0) { 'completed' } else { 'failed' }
        DurationSeconds = [Math]::Round(($finishedAt - $Run.StartedAt).TotalSeconds, 1)
        StdoutPath = $Run.StdoutPath
        StderrPath = $Run.StderrPath
    }
}

$prepared = @()
foreach ($layerName in $Layer) {
    $files = @(Get-AuditFiles -LayerName $layerName)
    if ($files.Count -eq 0) {
        throw "No audit files selected for $layerName"
    }
    $layerRoot = Join-Path $runRoot $layerName
    New-Item -ItemType Directory -Path $layerRoot -Force | Out-Null
    $inputPath = Join-Path $layerRoot 'input.md'
    New-LayerInput -LayerName $layerName -Files $files -InputPath $inputPath
    $prepared += [pscustomobject]@{
        Layer = $layerName
        FileCount = $files.Count
        InputPath = $inputPath
        StdoutPath = (Join-Path $layerRoot 'stdout.md')
        StderrPath = (Join-Path $layerRoot 'stderr.log')
    }
}

$codexCommand = Resolve-CodexCommand -Backend $AuthBackend -CustomLauncherPath $LauncherPath -ExecutablePath $CodexPath
$prepared | Select-Object Layer, FileCount, InputPath | Format-Table -AutoSize

if ($DryRun) {
    "Dry run backend: $AuthBackend"
    "Dry run executor: $($codexCommand.Description)"
    "Dry run complete. Prepared inputs: $runRoot"
    exit 0
}

$pending = [System.Collections.Generic.Queue[object]]::new()
$prepared | ForEach-Object { $pending.Enqueue($_) }
$running = @()
$results = @()
$lastProgressAt = Get-Date

while ($pending.Count -gt 0 -or $running.Count -gt 0) {
    while ($pending.Count -gt 0 -and $running.Count -lt $ThrottleLimit) {
        $next = $pending.Dequeue()
        "Starting $($next.Layer)"
        $running += Start-CodexAudit -CodexCommand $codexCommand -LayerName $next.Layer -InputPath $next.InputPath -StdoutPath $next.StdoutPath -StderrPath $next.StderrPath
    }

    if ($running.Count -gt 0 -and ((Get-Date) - $lastProgressAt).TotalSeconds -ge 15) {
        foreach ($run in $running) {
            $stdoutBytes = if (Test-Path -LiteralPath $run.StdoutPath) { (Get-Item -LiteralPath $run.StdoutPath).Length } else { 0 }
            $stderrBytes = if (Test-Path -LiteralPath $run.StderrPath) { (Get-Item -LiteralPath $run.StderrPath).Length } else { 0 }
            $elapsedSeconds = [Math]::Round(((Get-Date) - $run.StartedAt).TotalSeconds, 1)
            "Progress $($run.Layer): ${elapsedSeconds}s, stdout ${stdoutBytes}B, stderr ${stderrBytes}B"
        }
        $lastProgressAt = Get-Date
    }

    Start-Sleep -Milliseconds 500
    foreach ($run in @($running)) {
        $run.Process.Refresh()
        if (-not $run.Process.HasExited -and ((Get-Date) - $run.StartedAt).TotalMinutes -ge $TimeoutMinutes) {
            $run.TimedOut = $true
            $run.Process.Kill($true)
        }
        if ($run.Process.HasExited) {
            $result = Complete-CodexAudit -Run $run
            $results += $result
            "Finished $($result.Layer): $($result.Status) (exit $($result.ExitCode), $($result.DurationSeconds)s)"
            $running = @($running | Where-Object { $_ -ne $run })
        }
    }
}

$summary = @(
    '# Codex 分层验收运行摘要',
    '',
    ('运行目录：`{0}`' -f $runRoot),
    ('模型：`{0}`' -f $Model),
    ('认证后端：`{0}`' -f $AuthBackend),
    ('执行器：`{0}`' -f $codexCommand.Description),
    ('并发上限：`{0}`' -f $ThrottleLimit),
    '',
    '| 层 | 状态 | 退出码 | 耗时 | 标准输出 | 错误输出 |',
    '|---|---|---:|---:|---|---|'
)
foreach ($result in $results | Sort-Object Layer) {
    $summary += "| $($result.Layer) | $($result.Status) | $($result.ExitCode) | $($result.DurationSeconds)s | $($result.StdoutPath) | $($result.StderrPath) |"
}
[System.IO.File]::WriteAllLines((Join-Path $runRoot 'SUMMARY.md'), $summary, [System.Text.UTF8Encoding]::new($false))

"Run summary: $runRoot\SUMMARY.md"
if ($results.Status -contains 'failed' -or $results.Status -contains 'timeout') {
    exit 1
}
