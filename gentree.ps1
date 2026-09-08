param([string]$Path = ".", [int]$MaxDepth = 3, [string]$Prefix = "", [int]$Depth = 0)
$exclude = @('node_modules','.venv','venv','.git','.idea','.vscode','__pycache__','.qwen','date-fns')
$items = Get-ChildItem -Path $Path -Directory | Where-Object { $_.Name -notin $exclude }
for ($i = 0; $i -lt $items.Count; $i++) {
    $item = $items[$i]
    $isLast = $i -eq $items.Count - 1
    $connector = if ($isLast) { "└── " } else { "├── " }
    Write-Host "${Prefix}${connector}$($item.Name)"
    if ($Depth -lt $MaxDepth - 1) {
        $childPrefix = if ($isLast) { "${Prefix}    " } else { "${Prefix}│   " }
        & $PSCommandPath -Path $item.FullName -MaxDepth $MaxDepth -Prefix $childPrefix -Depth ($Depth + 1)
    }
}
