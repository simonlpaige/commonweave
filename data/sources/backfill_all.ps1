$script = "C:\Users\simon\.openclaw\workspace\ecolibrium\data\sources\wikidata_ingest.py"

# Countries already in our DB (non-US) + key countries we want
$countries = @(
    @("BO", "Bolivia"),
    @("EC", "Ecuador"),
    @("GY", "Guyana"),
    @("HN", "Honduras"),
    @("GT", "Guatemala"),
    @("NI", "Nicaragua"),
    @("NG", "Nigeria"),
    @("PY", "Paraguay"),
    @("SR", "Suriname"),
    @("VE", "Venezuela"),
    @("ZA", "South Africa"),
    @("AU", "Australia"),
    @("GB", "United Kingdom"),
    @("FR", "France"),
    @("DE", "Germany"),
    @("BR", "Brazil"),
    @("IN", "India"),
    @("MX", "Mexico"),
    @("CO", "Colombia"),
    @("CA", "Canada"),
    @("JP", "Japan"),
    @("NZ", "New Zealand"),
    @("SE", "Sweden"),
    @("NL", "Netherlands"),
    @("ES", "Spain"),
    @("IT", "Italy"),
    @("PE", "Peru"),
    @("CL", "Chile"),
    @("AR", "Argentina"),
    @("PH", "Philippines"),
    @("ID", "Indonesia"),
    @("TH", "Thailand"),
    @("EG", "Egypt"),
    @("GH", "Ghana"),
    @("ET", "Ethiopia"),
    @("TZ", "Tanzania"),
    @("UG", "Uganda"),
    @("RW", "Rwanda"),
    @("SN", "Senegal")
)

$total = $countries.Count
$i = 0
foreach ($c in $countries) {
    $i++
    $cc = $c[0]
    $name = $c[1]
    Write-Host "`n[$i/$total] $name ($cc)"
    python $script $cc $name 2>$null | Select-String -Pattern "Found|DB:|Done:"
    Start-Sleep -Seconds 3
}

Write-Host "`nBackfill complete!"
