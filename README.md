# Tema 1 Securitatea Informatiei
## Continut
1. [Necesitati](#Necesitati)
2. [Cum folosesc aplicatia](#Cum-folosesc-aplicatia)
3. [Prezentarea Algoritmului](#Prezentarea-Algoritmului)

## Necesitati
Am folosit python 3.8.3 si libraria `pycryptodome`.
Am avut unele probleme la folosirea librariei si daca aveti probleme la import-uri cred ca asta ar ajuta:
```py
pip uninstall crypto
pip uninstall pycryptodome
pip install pycryptodome
```
O modalitate de a accesa 3 console de exemplu `gitBash`.
## Cum folosesc aplicatia
Deschideti 3 console.
Primul pas este sa deschidem serverul `KM.py` astfel
```
python KM.py
```
In celelalte 2 console deschidem cei 2 clienti.
```
python Client.py
```
Acum vom juca rolul de client si vom alege ce mod de incriptare dorim (ECB sau CFB) scriind la linia de comanda optiunea si apasam enter.

Dupa aceea trebuie sa comunicam inceperea comunicarii scriind ceva si apoi apasand enter la tastatura.

Rezultatele vor fi scrise la ecran.

## Prezentarea algoritmului
### Modurile de criptare
Aceste moduri au fost implementare in modului `MyCryptography.py`. Exista 2 clase numite `ECB` si `CFB`. Fiecare clasa are metodele acestea principale:
>* init()     
> Initializeaza cifrul bloc folosit (AES)

>* _encrypt()   
> incripteaza un mesaj

>* _decrypt()   
> decripteaza un mesaj

>* pad()   
> adauga biti la sfaristul mesajului pentru a putea fi criptati

Am pus comentarii in cod care explica fiecare pas pentru fiecare functie unde este necesar. In mare functiile implementeaza exact diagramele din laboratoare si nu sunt foarte complexi.

Aceste clase sunt initializare si folosite atunci cand programele trimit mesaje prin sockets. Asta se intampla mai ales in interiorul claselor Request/Response unde mesajele sunt criptate si trimise.


### Comunicarea
Comunicarea are loc prin socket-uri. Urmeaza un model client-server. Am pus comentarii care idica ce se intampla exact si in cod. 

Cererile dintre client/server dar si raspunsurile au forma aceasta:
```py
request = Request({
    "code": int,
    "data": dict
}, cipher, iv)
```
`cipher` si `iv`sunt folosite pentru a determina ce mod se foloseste si cum sa initializam clasele ECB/CFB

In ansamblu acesta este lista de evenimente din aplicatie:
> Server: 
>* asculta, da accept si memoreaza clientii noi
>* gestioneaza cererile dupa campul `code`

Acestea sunt codurile si semnificatiile lor:
> Coduri:
> * 1 : Seteaza modul de criptare preferat
> * 2 : Cere ce mod de criptare s-a ales
> * 3 : Declara ca a terminat job-ul (scriere/citire)
> * 4 : Cere permisiunea de a continua

in functie de valoare codului face aceste actiuni:
> * 1 -> Seteaza pentru client modul preferat
> * 2 -> Verifica daca toti clientii si-au ales modul preferat. Daca da, trimite modul ales de server, daca nu, trimite un mesaj care indica clientului sa astepte si sa intrebe mai tarziu
> * 3 -> Seteaza un falg care indica faptul ca clientul a terminat job-ul(scriere/citire)
> * 4 -> Verifica daca toti clientii si-au facut job-ul(to write/ to read) si directioneaza urmatoarele actiuni ale clientilor, mai intai spune celui care trimite sa trimita apoi celui care citese sa citeasca.

Clientii fac urmatoarele lucruri:
>* Se conecteaza la server
>* Specifica modul preferat de criptare
>* Cere modul ales de server pana cand il primesc impreuna cu restul informatiilor necesare(cheia, vector initializare, rol)
>* Incepe comunicarea clientilor unul cu altul prin socket
>* Comunica cu serverul la fiecare 8 blocuri scrise/citire si asteapta semnalui de coordonare a serverului


