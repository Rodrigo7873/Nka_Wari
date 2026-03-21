---
description: Arrêter l'émulateur Android
---

// turbo
1. Arrêter tous les processus de l'émulateur (moteur qemu et interface).
run_command(CommandLine="Stop-Process -Name qemu-system-x86_64, emulator -Force -ErrorAction SilentlyContinue", Cwd="d:\Mes projet\N'ka_Wari", SafeToAutoRun=true, WaitMsBeforeAsync=0)
