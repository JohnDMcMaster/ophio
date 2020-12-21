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
    Sleep, 2000
    ; Close hex view
    Send {Esc}

    Sleep, 200

    return { "command": parsed.command }
}

BPSave(parsed)
{
    basename = parsed.basename

    ; file => save pattern as
    ; activate file menu
    ; send !f
    Send {Alt}
    Send {Down}
    Send {Down}
    Send {Down}
    Send {Down}
    send {Enter}
    ; save dialogue
    Sleep, 400
    fn := "%dirout%\%basename%"
    Send %fn%
    Sleep, 100
    send {Enter}
    Sleep, 100
    ; file format options: accept deafult
    send {Enter}
    
    Sleep, 200
    return { "command": parsed.command, "file": fn }
}

; https://autohotkey.com/board/topic/29293-closed-collection-of-beautiful-one-liner-codes/#entry187910
AscToHex(str,chr=1,n=0,mode=0)
{
   Return !mode ? (AscToHex(1,chr,asc(SubStr(str,chr,1)),1) . (chr < StrLen(str) ? AscToHex(str,chr+1) : "")) : ((n < 16 ? "" : AscToHex(1,chr,n//16,1)) . ((d:=mod(n,16)) < 10 ? d : Chr(d+55)))
}

BPTxFile(parsed)
{
    fn = parsed.file
    FileRead, contents, %fn%
    return { "command": parsed.command, "file": fn, "hex": AscToHex(contents) }
}

ProcessCommand(sock, line)
{
    Log("RX: " . line)
    ; MsgBox, %line%
    parsed := JSON.Load(line)
    command := parsed.command

    if (parsed.command == "reset") {
        reply := BPReset(parsed)
    } else if (parsed.command == "about") {
        reply := BPAbout(parsed)
    } else if (parsed.command == "read") {
        reply := BPRead(parsed)
    } else if (parsed.command == "show") {
        reply := BPShow(parsed)
    } else if (parsed.command == "save") {
        reply := BPSave(parsed)
    } else if (parsed.command == "tx_file") {
        reply := BPTxFile(parsed)
    } else {
        reply := { "command": parsed.command, "error": 1, "message": "Invalid command" }
    }
    reply := JSON.Dump(reply)
    Log("TX: " . reply)
    Sock.SendText(reply . "`n")
}

OnAccept(Server)
{
    sock := Server.Accept()
    ; Doesn't seem to detect closed sockets correctly
    ; Work around by timing out for idle
    sock.Blocking := False
    ; aha! timeout of 0 doesn't detect closed socket
    ; but an arbitrarily long timeout does instantly
    ; set it long enough to still allow manual testing for now
    sock.BlockSleep := 60000

    while line := sock.RecvLine()
        ProcessCommand(sock, line)

    Sock.Disconnect()
}

OnExit()
{
    Log("Exiting at " . TimeStr())
    ExitApp
}

StartDateTime := TimeStr()
basedir = F:\buffer\ahk\out
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

Log("Starting server at " . StartDateTime)


Server := new SocketTCP()
Server.OnAccept := Func("OnAccept")
Server.Bind(["0.0.0.0", 1337])
Server.Listen()


Esc::
Onexit()
return
