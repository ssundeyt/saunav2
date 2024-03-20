# saunav2 - AFBostäder mobbning
Grymt skript för tidsbokning av bastu!

# Release 1.0.0 + patch
Alla basfunktioner är definierade och skriptet är nu en release!

Buggar som uppstod vid testning (speciellt av for loopen) är fixade.

# Sammanfattning + guide
**Attributer:**

Requests - för inloggning. Enklare än att använda selenium för inloggning

Selenium - Simulerar bokning genom webbläsaren. (Firefox)

BeautifulSoup - Lagrar cookies för att passa till selenium

GetPass - Säkrare användning av passphrases i skriptet. (säkrare än afbostäder :P)

**Beskrivning av skripten**

Det finns 2 olika, main main och simplifierad main.

Den simplifierade versionen bokar alltid söndag 20-23, den testar först söndag denna vecka, sedan söndag nästa vecka. Fungerar ingen av dom tiderna kommer en for loop köras som kontinuerligt checkar dessa två datum tills att ett av dom öppnas upp, främst för att norpa tider vid avbokning. Loopen körs tills tid bokats av skriptet eller tills du avbryter den.
_Notera att du måste ändra till din egen mail och lösenord i koden för skriptet för att det ska köras_

Main versionen har till viss del samma funktion som den simplifierade. Skillnaden är att ett ui finns där användaren själv skriver in lösenord och mail, väljer datum och tid sen körs loopen. Tanken är att flera personer ska kunna ladda ner skriptet och köra det utan att veta hur man ändrar dessa attributer i python. (amatörer :D)

**För att köra skripten:**

Steg 1. Klona giten eller ladda ner projekten till din maskin. öppna terminalen och cd in i foldern. pip install -r requirements.txt. 

Steg 2. Eftersom vi använder firefox för att simulera bokning måste du a) Ladda ned firefox. b) ladda ned geckodriver för ditt operativsystem.

Steg 2.1 Gå hit: https://github.com/mozilla/geckodriver/releases. 

_för win; tryck "show all assets" under "assets" och ladda ned geckodriver-v0.34.0-win64.zip. Extrahera filen och lägg .exe i C:\Windows_

_för macosx; Gå till samma sida men ladda ned "geckodriver-v0.34.0-macos.tar.gz". extrahera och lägg .exe i C:\usr\local\bin_

Nu kan du starta det skript du vill köra!


contributors och pull requests alltid välkommna. Push request = block :D
