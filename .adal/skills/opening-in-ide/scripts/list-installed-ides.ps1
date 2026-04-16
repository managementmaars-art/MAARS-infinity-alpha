#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (Get-Command rider -ErrorAction SilentlyContinue -CommandType Application) {
    'rider'
}
elseif (Get-Command rider.bat -ErrorAction SilentlyContinue -CommandType Application) {
    'rider'
}
elseif (Get-Command rider64.exe -ErrorAction SilentlyContinue -CommandType Application) {
    'rider'
}

if (Get-Command webstorm -ErrorAction SilentlyContinue -CommandType Application) {
    'webstorm'
}
elseif (Get-Command webstorm.bat -ErrorAction SilentlyContinue -CommandType Application) {
    'webstorm'
}
elseif (Get-Command webstorm64.exe -ErrorAction SilentlyContinue -CommandType Application) {
    'webstorm'
}

if (Get-Command code -ErrorAction SilentlyContinue -CommandType Application) {
    'code'
}
elseif (Get-Command code.cmd -ErrorAction SilentlyContinue -CommandType Application) {
    'code'
}

if (Get-Command cursor -ErrorAction SilentlyContinue -CommandType Application) {
    'cursor'
}
elseif (Get-Command cursor.cmd -ErrorAction SilentlyContinue -CommandType Application) {
    'cursor'
}

if (Get-Command windsurf -ErrorAction SilentlyContinue -CommandType Application) {
    'windsurf'
}
elseif (Get-Command windsurf.cmd -ErrorAction SilentlyContinue -CommandType Application) {
    'windsurf'
}
