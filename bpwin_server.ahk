/*
BPWin remote control server via AutoHotKey 
Allows remote scripts to script GUI operations such as reading and writing data

Based on:
https://github.com/cocobelgica/AutoHotkey-JSON
https://github.com/G33kDude/Socket.ahk/
*/

#Include %A_LineFile%\..\JSON.ahk
#Include Socket.ahk
#NoEnv
SetBatchLines, -1
CoordMode, Mouse, Screen

basedir = C:\buf\rom\ahk\out




StartDateTime := TimeStr()
dirout = %basedir%\%StartDateTime%
dirout = %basedir%
FileCreateDir, %dirout%
fn = %dirout%\log.txt
logfile := FileOpen(fn, "w")
if !IsObject(logfile)
{
    MsgBox Can't open "%fn%" for writing.
    return
}


TimeStr()
{
    FormatTime, StartDateTime, %A_NowUTC%, yyyy-MM-dd_HH.mm.ss
    return StartDateTime
}
Log(msg)
{
    global logfile
    logfile.Write(msg)
    logfile.Write("`n")
    logfile.Read(0)
}

BPReset(parsed)
{
    ; clear abnormal condition (if any)
    ; ex: overcurrent during read, file choser

    Send {Esc}
    Sleep, 200

    Send {Esc}
    Sleep, 200

    WinActivate
    
    return { "command": parsed.command }
}

BPAbout(parsed)
{
    ; help => about
    Send !h
    Send {Down}
    Send {Down}
    Send {Down}
    send {Enter}
    Sleep, 200

    ; V5.33.0 (7/16/2013)
    ; Algo DB Rev. 0
    ; etc
    ; WinGetText message, ahk_class #32770
    WinGetText message, About BPWin

    ; Send {Esc}
    send {Enter}
    Sleep, 200
    
    return { "command": parsed.command, "about": message }
}

BPRead(parsed)
{
    ;initiate read
    send {SPACE}
    Sleep, 2000

    ; chip inserted backwards, not in socket, etc
    if WinExist("ahk_class #32770") {
        WinGetText message, ahk_class #32770

        ; clear abnormal condition (if any)
        ; ex: overcurrent during read
        Send {Esc}
        Sleep, 200
        return { "command": parsed.command, "error": 1, "message": message }
    }

    return { "command": parsed.command }
}

BPProgram(parsed)
{
    ;initiate write
    send {SPACE}
	; about 1200
    Sleep, 1500

	; clear confirmation
    send {SPACE}
	; about 4000
    Sleep, 5000

    return { "command": parsed.command }
}

BPShow(parsed)
{
    ; activate data view
    send ^e
    ; select hex view
    ; bytes instead of words
    send {Tab}
    send B
    Sleep, 200
    ; hex address instead of dec
    send {Tab}
    send {Tab}
    send X
    send {Up}
    ; let user oogle the data
    Sleep, parsed.ms
    ; Close hex view
    Send {Esc}

    Sleep, 200

    return { "command": parsed.command }
}

BPSave(parsed)
{
	global dirout
    basename := parsed.basename
    fn := dirout . "\" . basename

    ; file => save pattern as
    ; activate file menu
    ; send !f
    Send {Alt}
    Sleep, 50
    Send {Down}
    Sleep, 10
    Send {Down}
    Sleep, 10
    Send {Down}
    Sleep, 10
    Send {Down}
    Sleep, 10
    send {Enter}
    Sleep, 10
    ; save dialogue
	WinWait, Save As, , 3
	if (ErrorLevel != 0)
	{
		return { "command": parsed.command, "error": 1, "message": "Save As timeout" }
	}
    Sleep, 100

    Send %fn%
    Sleep, 200
    send {Enter}
    Sleep, 200

	; Already exists
    if WinExist("Confirm Save As") {
		Send {Left}
		send {Enter}
		Sleep, 200
	}

	WinWait, Save Data Pattern File, , 3
	if (ErrorLevel != 0)
	{
		return { "command": parsed.command, "error": 1, "message": "Save Data Pattern File timeout" }
	}

    ; file format options: accept deafult
    send {Enter}
    
    Sleep, 300
    return { "command": parsed.command, "file": fn }
}

BPOpen(parsed)
{
	global dirout
    basename := parsed.basename
    fn := dirout . "\" . basename

    ; file => save pattern as
    ; activate file menu
    ; send !f
    Send {Alt}
    Sleep, 50
    Send {Down}
    Sleep, 10
    Send {Down}
    Sleep, 10
    send {Enter}
    Sleep, 10
    ; open dialogue
	WinWait, Open, , 3
	if (ErrorLevel != 0)
	{
		return { "command": parsed.command, "error": 1, "message": "Open timeout" }
	}
    Sleep, 100

    Send %fn%
    Sleep, 200
    send {Enter}
    Sleep, 200


	WinWait, Load Data Pattern File, , 3
	if (ErrorLevel != 0)
	{
		return { "command": parsed.command, "error": 1, "message": "Load Data Pattern File timeout" }
	}

    ; file format options: accept deafult
    send {Enter}
    
    Sleep, 300
    return { "command": parsed.command, "file": fn }
}

Nib2Hex(n)
{
    return n < 10 ? Chr(48 + n) : Chr(55 + n)
}

Char2Hex(c)
{
    n := asc(c)
    l := Nib2Hex(n >> 4)
    r := Nib2Hex(n & 0xF)
    return l . r
}

U82Hex(n)
{
    l := Nib2Hex(n >> 4)
    r := Nib2Hex(n & 0xF)
    return l . r
}

Hex2Nib(c)
{
	; FIXME
	return 0
}

Hex2U8(buf)
{
    l := Hex2Nib(SubStr(buf, 0, 1))
    r := Hex2Nib(SubStr(buf, 1, 1))
	return (l << 4) | r
}

/*
AHK v1 doesn't handle binary data well
This function is inherently unsafe without immediately converting to hex
Instead load to hex string

Str2Hex(str)
{
	ret := ""
	; doesn't work correctly on binary data
	; Loop, Parse, str
	i := 0
	while (i < StrLen(str))
	{
		c := SubStr(str, A_Index, 1)
		ret := ret . Char2hex(c)
		i := i + 1
	}
	return ret
}
*/

Fn2Hex(fn)
{
	f := FileOpen(fn, "r")
	if (ErrorLevel != 0)
	{
		return ""
	}

	ret := ""
	; FIXME: this might be a memory leak
	while (n := f.rawRead(cbuf, 1))
	{
		n := NumGet(cbuf, "UChar")
		; ret := ret . Char2hex(cbuf)
		ret := ret . U82Hex(n)
	}
	f.close()
	return ret
}

Hex2Fn(hex, fn)
{
	f := FileOpen(fn, "w")
	if (ErrorLevel != 0)
	{
		return ""
	}

	i := 0
	while (i < 6)
	{
		buf = SubStr(hex, i, 2)
		u8 = Hex2U8(buf)
		f.RawWrite(u8, 1)
		i := i + 2
	}

	f.close()
}

BPTxFile(parsed)
{
	global dirout
    basename := parsed.basename
    fn := dirout . "\" . basename

    return { "command": parsed.command, "file": fn, "hex": Fn2Hex(fn) }
}

BPRxFile(parsed)
{
	; FIXME
	; end application is working around by using network share for now

	global dirout
    basename := parsed.basename
    fn := dirout . "\" . basename

    Hex2Fn(hex, fn)
}

ProcessCommand(sock, line)
{
    Log("RX: " . line)
    ; MsgBox, %line%
    parsed := JSON.Load(line)
    command := parsed.command

    if (parsed.command == "reset") {
        reply := BPReset(parsed)
    } else if (parsed.command == "reload") {
		Reload
        reply := { "command": parsed.command }
    } else if (parsed.command == "nop") {
        reply := { "command": parsed.command }
    } else if (parsed.command == "about") {
        reply := BPAbout(parsed)
    } else if (parsed.command == "read") {
        reply := BPRead(parsed)
    } else if (parsed.command == "program") {
        reply := BPProgram(parsed)
    } else if (parsed.command == "show") {
        reply := BPShow(parsed)
    } else if (parsed.command == "save") {
        reply := BPSave(parsed)
    } else if (parsed.command == "open_data") {
        reply := BPOpen(parsed)
    } else if (parsed.command == "tx_file") {
        reply := BPTxFile(parsed)
    } else if (parsed.command == "rx_file") {
        reply := BPRxFile(parsed)
    } else {
        reply := { "command": parsed.command, "error": 1, "message": "Invalid command" }
    }
    reply := JSON.Dump(reply)
    Log("TX: " . reply)
    Sock.SendText(reply . "`n")
	
	; Hack: memory leaks and other issues
	; Reload
}

OnAccept(Server)
{
    sock := Server.Accept()
    ; Doesn't seem to detect closed sockets correctly
    ; Work around by timing out for idle manually
    sock.Blocking := False
    ; aha! timeout of 0 doesn't detect closed socket
    ; but an arbitrarily long timeout does instantly
    ; set it long enough to still allow manual testing for now
    ; sock.BlockSleep := 1000

	; 2020-12-21: I misinterpreted the original issue here
	; might be able to revert this to the original AHK timeout code,
	; but IMHO this is slightly better overall
	timeout := 60000
	last := A_TickCount
	Log("Connect @ " . last)
    while (A_TickCount - last < timeout)
	{
		line := sock.RecvLine()
		if (line)
		{
			ProcessCommand(sock, line)
			last := A_TickCount
			; Log("Finished command @ " . last)
		} else {
			Sleep, 10
			; Log("Timeout command @ " . A_TickCount)
		}
	}

	Log("Disconnect @ " . A_TickCount)
    Sock.Disconnect()
}

OnExit()
{
    Log("Exiting at " . TimeStr())
    ExitApp
}


Log("Starting server at " . StartDateTime)


Server := new SocketTCP()
Server.OnAccept := Func("OnAccept")
Server.Bind(["0.0.0.0", 13377])
Server.Listen()


Shift::
Onexit()
return
