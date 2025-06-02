# Script para actualizar todos los archivos de ejercicios
# Ubicación relativa a la carpeta static
$ejerciciosPath = Join-Path $PSScriptRoot '..\ejercicios'
$backupPath = Join-Path $ejerciciosPath 'backup'

# Crear directorio de respaldo si no existe
if (-not (Test-Path $backupPath)) {
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
}

# Obtener todos los archivos HTML de ejercicios
$archivos = Get-ChildItem -Path $ejerciciosPath -Recurse -Filter '*.html' | Where-Object { $_.FullName -notlike '*\backup\*' }

foreach ($archivo in $archivos) {
    $nombreArchivo = $archivo.Name
    $rutaCompleta = $archivo.FullName
    $rutaBackup = Join-Path $backupPath $nombreArchivo
    
    Write-Host 'Procesando: ' $nombreArchivo -ForegroundColor Cyan
    
    # Crear copia de respaldo
    Copy-Item -Path $rutaCompleta -Destination $rutaBackup -Force
    Write-Host '  - Backup creado: ' $rutaBackup -ForegroundColor Green
    
    # Leer el contenido del archivo
    $contenido = Get-Content -Path $rutaCompleta -Raw
    
    # Reemplazar la redirección por window.close()
    $patron = 'window\\.location\\.href\\s*=\\\s*[''"].*?/estudiantes/ejercicios[''"]\\s*;?'
    $nuevoContenido = $contenido -replace $patron, 'window.close();'
    
    # Si hubo algún cambio, guardar el archivo
    if ($nuevoContenido -ne $contenido) {
        $nuevoContenido | Set-Content -Path $rutaCompleta -NoNewline -Encoding UTF8
        Write-Host '  - Archivo actualizado correctamente' -ForegroundColor Green
    } else {
        Write-Host '  - No se realizaron cambios en el archivo' -ForegroundColor Yellow
    }
    
    Write-Host ''
}

Write-Host 'Proceso completado. Se han actualizado todos los archivos de ejercicios.' -ForegroundColor Green
Write-Host 'Las copias de seguridad se encuentran en: ' $backupPath -ForegroundColor Green
