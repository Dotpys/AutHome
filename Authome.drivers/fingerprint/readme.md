# FingerLib

## Implemented instructions

|OpCode|Mnemonic|Description|Status|
|------|--------|-----------------|------|
|0x01|GenImg|Genera un'immagine dell'impronta digitale|🟢|
|0x02|Img2Tz|Genera le caratteristiche dell'impronta|🟢|
|0x03|Match|Confronta i due buffer di caratteristiche sul modulo|🟢|
|0x04|Search||🟡|
|0x05|RegModel||🔴|
|0x06|Store||🔴|
|0x07|LoadChar||🔴|
|0x08|UpChar||🔴|
|0x09|DownChr||🔴|
|0x0A|UpImage|Il sensore di impronta carica l'immagine sul controller|🟢|
|0x0B|DownImage||🔴|
|0x0C|DeleteChar||🔴|
|0x0D|Empty||🔴|
|0x0E|SetSysPara||🔴|
|0x0F|ReadSysPara|Legge i parametri del modulo|🟢|
|0x12|SetPwd||🔴|
|0x13|VfyPwd||🔴|
|0x14|GetRandomCode||🔴|
|0x15|SetAdder||🔴|
|0x1D|TempleteNum||🔴|
|0x1F|ReadConList||🔴|