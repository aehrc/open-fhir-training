# Power BI reports

This folder contains a Power BI report for each of the studies in this
repository, and a fifth report that demonstrates DirectQuery. Each report reads
the views and queries that the notebooks and SQL files create in Databricks,
using the Databricks connector for Power BI.

The reports are saved as
[Power BI projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
(`.pbip`). The semantic model is stored as TMDL files and the report as PBIR
JSON files, so changes can be reviewed and compared in Git. No data is stored in
the repository.

| Report | Databricks source | Storage mode |
|---|---|---|
| `ProstateCancerRiskFactors` | View `synthea_prostate_cancer_views.prostate_cancer_risk_factors`, joined to the FHIR `synthea.patient` table for gender | Import |
| `MiSecondaryPrevention` | View `synthea_mi_secondary_prevention_views.mi_secondary_prevention`, and the summary query from `sql/synthea/combine_mi_secondary_prevention_views.sql` | Import |
| `PulseOximetryBias` | Views `mimic_iv_views.coh_subject`, `coh_reading_spo2` and `coh_reading_so2`, and a query that pairs each SaO2 with the preceding SpO2 | Import |
| `BetaBlockerSepticShock` | View `mimic_iv_beta_blocker_views.beta_blocker_septic_shock`, and the summary query from `sql/mimic_iv/combine_beta_blocker_septic_shock_views.sql` | Import |
| `DirectQueryDemo` | View `synthea_mi_secondary_prevention_views.mi_secondary_prevention` | DirectQuery |

## Requirements

- Power BI Desktop, May 2026 release or later (earlier releases do not support
  the PBIR file versions used here)
- Access to a Databricks workspace in which the views have been created (see the
  main [README](../README.md)), and a SQL warehouse to query them with

## Opening a report

1. Open the `.pbip` file in the report's folder, for example
   `MiSecondaryPrevention/MiSecondaryPrevention.pbip`.
2. The visuals are empty until the data is loaded. Click **Refresh now** on the
   yellow bar.
3. The first time you connect, Power BI asks for credentials for the SQL
   warehouse. Choose **OAuth (OIDC)** and sign in with your Databricks account.
   Power BI keeps the credential for the warehouse, so the other reports reuse
   it.
4. Reports that run their own SQL ask you to approve each native database query.
   Click **Run**.

If your Databricks login uses a passkey stored in a password manager, set
**File > Options and settings > Options > Global > Security > Authentication
Browser** to **Use my default web browser** before signing in. The browser built
into Power BI cannot use passkeys from a password manager's browser extension.

The DirectQuery report has no data to load, so it does not show the **Refresh
now** bar. It asks for credentials the first time a visual queries Databricks.

## Connecting to a different workspace

Each report has two parameters that identify the SQL warehouse:
`DatabricksHost` and `DatabricksHttpPath`. They are set to the CSIRO training
workspace. To use another workspace, open **Transform data > Edit parameters**
and enter the **Server hostname** and **HTTP path** from the **Connection
details** tab of your SQL warehouse in Databricks. Then refresh.

The views are read from the `hive_metastore` catalog. If you created them in
another catalog, change `"hive_metastore"` in each table's query in **Transform
data**.

## How the reports connect to Databricks

### Views

A table that reads a view navigates from the warehouse to the catalog, schema
and view. This is the Power Query (M) code of the `Cohort` table in
`MiSecondaryPrevention`:

```
let
    Source = DatabricksMultiCloud.Catalogs(DatabricksHost, DatabricksHttpPath, [Catalog = null, Database = null, EnableAutomaticProxyDiscovery = null]),
    Catalog = Source{[Name = "hive_metastore"]}[Data],
    Schema = Catalog{[Name = "synthea_mi_secondary_prevention_views"]}[Data],
    Data = Schema{[Name = "mi_secondary_prevention"]}[Data],
    ...
```

This is the code that Power BI generates when you choose **Get data >
Databricks** and select the view in the navigator. Power BI translates the
later steps into SQL where it can (query folding), so the warehouse does the
filtering and column selection.

### Queries

A table can also run a SQL query of your own with `Value.NativeQuery`. The
`Summary query` table in `MiSecondaryPrevention` runs the summary query from
`sql/synthea/combine_mi_secondary_prevention_views.sql`, with the Power BI
parameter `FollowUpDays` in place of the SQL parameter `:follow_up_days`:

```
Query = Value.NativeQuery(Catalog, "WITH treated AS ( ... COALESCE(days <= " & Number.ToText(FollowUpDays) & ", FALSE) AS treated ...", null, [EnableFolding = true])
```

To change the window, edit the `FollowUpDays` parameter and refresh. The other
visuals in the report apply the window with DAX measures over the days columns
of the view, so the **Follow-up window** slicer changes them without a refresh.
The report shows both approaches side by side.

To add a query of your own, open **Transform data**, duplicate the `Summary
query` table, open its **Advanced editor** and replace the SQL text.

### Import and DirectQuery

The four study reports use Import mode: a refresh copies the rows into the
report, and the visuals query that copy. The warehouse only needs to be running
during a refresh.

`DirectQueryDemo` uses DirectQuery mode: every visual sends SQL to the warehouse
each time it renders, so the warehouse must be running while the report is in
use. The connection sets the query tag `source:powerbi-directquery-demo`, so you
can see the SQL that Power BI generates in the warehouse's **Query history**, or
with this query:

```sql
SELECT start_time, statement_text
FROM system.query.history
WHERE query_tags['source'] = 'powerbi-directquery-demo'
ORDER BY start_time DESC
```
