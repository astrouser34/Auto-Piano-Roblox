
#Requires AutoHotkey v2.0
#NoTrayIcon


activo := false
pausado := false
bucle := false
delay := 120
delayGuion := 1000

teclasBloqueadas := ["/", "Esc", "Enter", "Tab", "F1", "F2", "F3", "F4"]

; ===== GUI =====
miGui := Gui("+Resize")
miGui.Title := "🎹 AutoPiano Roblox"

miGui.SetFont("s10", "Segoe UI")

miGui.AddText("xm", "Partitura:")
caja := miGui.AddEdit("xm w420 h180")

miGui.AddText("xm y+10", "Velocidad notas")
slider := miGui.AddSlider("xm w300 Range20-400", delay)
textoVel := miGui.AddText("x+10 w70", delay " ms")

miGui.AddText("xm y+10", "Tiempo pausa (-)")
sliderGuion := miGui.AddSlider("xm w300 Range100-3000", delayGuion)
textoGuion := miGui.AddText("x+10 w80", delayGuion " ms")

estado := miGui.AddText("xm y+10 cBlue", "Estado: Detenido")

btnPlay := miGui.AddButton("xm w120", "▶ Iniciar (F8)")
btnPause := miGui.AddButton("x+10 w120", "⏸ Pausa (F6)")
btnStop := miGui.AddButton("x+10 w120", "⏹ Detener (F7)")
btnLoop := miGui.AddButton("xm y+10 w250", "🔁 Bucle infinito: OFF (F5)")

slider.OnEvent("Change", CambiarVelocidad)
sliderGuion.OnEvent("Change", CambiarGuion)

btnPlay.OnEvent("Click", Iniciar)
btnPause.OnEvent("Click", Pausar)
btnStop.OnEvent("Click", Detener)
btnLoop.OnEvent("Click", ToggleLoop)

miGui.Show()

; ===== FUNCIONES =====

EstaBloqueada(tecla)
{
    global teclasBloqueadas
    for t in teclasBloqueadas
        if (t = tecla)
            return true
    return false
}

CambiarVelocidad(*)
{
    global slider, textoVel, delay
    delay := slider.Value
    textoVel.Text := delay " ms"
}

CambiarGuion(*)
{
    global sliderGuion, textoGuion, delayGuion
    delayGuion := sliderGuion.Value
    textoGuion.Text := delayGuion " ms"
}

Iniciar(*)
{
    global caja, delay, delayGuion, activo, pausado, estado, bucle

    if activo
        return

    activo := true
    pausado := false
    estado.Text := "Estado: Reproduciendo"

    partitura := caja.Value

    while activo
    {
        i := 1

        while (i <= StrLen(partitura))
        {
            if (!activo)
                break

            while pausado
                Sleep 50

            letra := SubStr(partitura, i, 1)

            if (letra = " " || letra = "`n" || letra = "`r")
            {
                i++
                continue
            }

            if (letra = "-")
            {
                Sleep delayGuion
                i++
                continue
            }

            if (letra = "[")
            {
                acorde := ""
                i++

                while (i <= StrLen(partitura) && SubStr(partitura, i, 1) != "]")
                {
                    acorde .= SubStr(partitura, i, 1)
                    i++
                }

                for tecla in StrSplit(acorde)
                    if !EstaBloqueada(tecla)
                        Send "{" tecla " down}"

                Sleep 40

                for tecla in StrSplit(acorde)
                    if !EstaBloqueada(tecla)
                        Send "{" tecla " up}"

                Sleep delay
                i++
                continue
            }

            if !EstaBloqueada(letra)
            {
                Send letra
                Sleep delay
            }

            i++
        }

        if !bucle
            break
    }

    estado.Text := "Estado: Detenido"
    activo := false
}

Pausar(*)
{
    global pausado, activo, estado

    if !activo
        return

    pausado := !pausado

    if pausado
        estado.Text := "Estado: Pausado"
    else
        estado.Text := "Estado: Reproduciendo"
}

Detener(*)
{
    global activo, pausado, estado

    activo := false
    pausado := false
    estado.Text := "Estado: Detenido"
}

ToggleLoop(*)
{
    global bucle, btnLoop

    bucle := !bucle

    if bucle
        btnLoop.Text := "🔁 Bucle infinito: ON (F5)"
    else
        btnLoop.Text := "🔁 Bucle infinito: OFF (F5)"
}

; ===== HOTKEYS =====

F8::Iniciar()
F6::Pausar()
F7::Detener()
F5::ToggleLoop()