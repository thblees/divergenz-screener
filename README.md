# S&P 500 Divergenz-Screener

Scannt jeden Handelstag nach US-Boersenschluss alle S&P-500-Aktien auf
bullische RSI(14)-Divergenzen (regulaer und versteckt, Tageschart) und
veroeffentlicht das Ergebnis als Dashboard auf GitHub Pages.

## Einmalige Einrichtung (ca. 10 Minuten)

**1. GitHub-Account anlegen** (falls noch nicht vorhanden):
https://github.com/signup

**2. Neues Repository anlegen:** https://github.com/new
- Repository name: `divergenz-screener`
- Sichtbarkeit: **Public** (noetig fuer kostenloses GitHub Pages)
- Sonst nichts anhaken, "Create repository" klicken

**3. Dateien hochladen:**
- ZIP entpacken. Wichtig: Der Ordner `.github` ist versteckt -
  im Windows-Explorer unter "Anzeigen" die Option
  "Ausgeblendete Elemente" aktivieren.
- Im neuen Repository auf den Link "uploading an existing file" klicken
  und ALLE Dateien und Ordner aus dem ZIP ins Browserfenster ziehen
  (Chrome/Edge uebernehmen die Ordnerstruktur).
- Unten "Commit changes" klicken.
- Falls der `.github`-Ordner sich nicht hochladen laesst: Im Repository
  "Add file" -> "Create new file", als Dateinamen
  `.github/workflows/scan.yml` eintippen und den Inhalt der Datei
  per Copy & Paste einfuegen.

**4. GitHub Pages aktivieren:**
- Im Repository: Settings -> Pages
- Unter "Build and deployment" bei "Source": **GitHub Actions** waehlen

**5. Ersten Lauf starten:**
- Tab "Actions" oeffnen (ggf. Workflows einmalig freigeben)
- Links "Taeglicher Divergenz-Scan" waehlen -> "Run workflow"
- Nach ca. 3-5 Minuten ist das Dashboard online unter:
  `https://DEIN-BENUTZERNAME.github.io/divergenz-screener/`

## Danach laeuft alles automatisch

Der Zeitplan steht in `.github/workflows/scan.yml`:
Montag bis Freitag um 21:30 UTC (23:30 deutsche Sommerzeit,
22:30 Winterzeit), also nach US-Boersenschluss. GitHub-Cron kann
sich um einige Minuten verzoegern - das ist normal.

## Methodik

- **Fruehsignal:** Das zweite Tief stammt aus den letzten 2 Handelstagen
  (RSI auf Basis des letzten Schlusskurses), ist das tiefste der letzten
  12 Bars, aber noch nicht klassisch bestaetigt - es kann an den
  Folgetagen unterschritten werden.
- **Bestaetigt:** Pivot-Tief mit 3 Bars rechts.
- **Regulaer:** tieferes Preistief bei hoeherem RSI-Tief (mind. ein
  RSI-Tief unter 45) - moegliche Umkehr.
- **Versteckt:** hoeheres Preistief bei tieferem RSI-Tief, nur bei Kurs
  ueber SMA50 - moegliche Trendfortsetzung.
- Staerke-Filter: RSI-Differenz >= 3 Punkte, Tief-Differenz >= 0,5 %.
- Datenquelle: Yahoo Finance (adjustierte Kurse). Die Ticker-Liste
  (`sp500-ticker.txt`) bei Index-Aenderungen gelegentlich aktualisieren.

Kein Anlageberatungs-Tool - eine Divergenz ist ein Hinweis, kein Signal
fuer sich allein.
