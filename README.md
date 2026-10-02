# Controllo Timbrature - Cartellino

Form per controllo timbrature giornaliere come da gestionale HR.

Basato sull'immagine originale con colonne: GIO., MOD., E, U, DOV, EFF, -/+, STR, TURNO, B.P., GIUSTIFICATIVI.

## Funzioni
- Inserimento E/U (Entrata/Uscita) con formato HH:MM
- Domeniche in rosso, MOD. PM001 / PMFSNL automatico
- Salvataggio CSV ed Excel
- Icona personalizzabile (`icona.ico`)

## Avvio locale (Windows 7 / 10 / 11)

```bash
pip install -r requirements.txt
python cartellino.py
```

## Creare EXE con nuova icona
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icona.ico cartellino.py
```

## Mettere online con GitHub Pages (versione web)
Il progetto include anche `index.html` per la versione web interattiva.
Abilita GitHub Pages su `main` branch.

## Aggiornamenti
Per aggiornare il programma:
1. Modifica `cartellino.py`
2. `git add .`
3. `git commit -m "aggiornamento"`
4. `git push`
