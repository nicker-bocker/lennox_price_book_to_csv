# Instructions

## Initial setup
1. `pip install -r requirements.txt`


## York
1. Export Excel to csv. https://www.extendoffice.com/documents/excel/2980-excel-save-export-each-sheet-as-csv.html#vba
```
Public Sub SaveWorksheetsAsCsv()
    Dim xWs As Worksheet
    Dim xDir As String
    Dim folder As FileDialog
    Set folder = Application.FileDialog(msoFileDialogFolderPicker)
    If folder.Show <> -1 Then Exit Sub
    xDir = folder.SelectedItems(1)
    For Each xWs In Application.ActiveWorkbook.Worksheets
    xWs.SaveAs xDir & "\" & xWs.Name, xlCSV
    Next
End Sub
```
2. ensure price csv files are in a directory named `./york` in the script path
3. run `python york_price_scraper.py`
4. get the output; `york_results.csv` in the same directory as script


## Lennox

1. Highlight and copy all text in price book pdf using adobe reader
2. Paste in a new text file named "lennox_dna.txt" and save as ANSI in the same directory as the script
3. run `python lennox_price_scraper.py`
4. get the output; `lennox_results.csv` in the same directory as script


## Trane

1. Highlight and copy all text in price book pdf using adobe reader
2. Paste in a new text file named "lennox_dna.txt" and save as ANSI in the same directory as the script
3. run `python trane_price_scraper.py`
4. get the output; `trane_results.csv` in the same directory as script