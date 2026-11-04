---
title: Ladeinfrastruktur in Deutschland
---

```sql meta
select
    strftime(bnetza_stand, '%d.%m.%Y') as bnetza_stand,
    kba_stand,
    strftime(update, '%Y-%m-%d') as update
from shared.meta
```

<p class="text-sm text-base-content-muted mb-6">
Datenstand: BNetzA: {meta[0].bnetza_stand} | KBA: {meta[0].kba_stand} (Update: {meta[0].update})
</p>

```sql states
select 'Alle Bundesländer' as bundesland, 0 as sort_key
union all
select distinct bundesland, 1 as sort_key from shared.overview
order by sort_key, bundesland
```

<Dropdown
    data={states}
    name=bundesland
    value=bundesland
    title="Bundesland"
    defaultValue="Alle Bundesländer"
/>

<Dropdown name=typ title="Leistungstyp" multiple=true selectAllByDefault=true>
    <DropdownOption value="hpc" valueLabel="HPC-Laden (>= 150 kW)"/>
    <DropdownOption value="schnell" valueLabel="Schnellladen (> 22 kW)"/>
    <DropdownOption value="normal" valueLabel="Normalladen (<= 22 kW)"/>
</Dropdown>

```sql filtered
-- The selected categories as flags; an empty selection makes all three false,
-- which yields zeros and the hint instead of a query error.
with selection as (
    select
        'hpc' in ${inputs.typ.value} as sel_hpc,
        'schnell' in ${inputs.typ.value} as sel_schnell,
        'normal' in ${inputs.typ.value} as sel_normal
)

select
    jahr,
    stationen,
    kw,
    sel_hpc,
    sel_schnell,
    sel_normal,
    (has_hpc and sel_hpc) or (has_schnell and sel_schnell) or (has_normal and sel_normal) as matches,
    case when sel_hpc then lp_hpc else 0 end as lp_hpc,
    case when sel_schnell then lp_schnell else 0 end as lp_schnell,
    case when sel_normal then lp_normal else 0 end as lp_normal
from shared.overview, selection
where '${inputs.bundesland.value}' in ('Alle Bundesländer', bundesland)
```

```sql kpis
-- Numbers are formatted as German text here because Evidence formats with
-- English separators only.
select
    replace(format('{:,}', coalesce(sum(stationen) filter (where matches), 0)::bigint), ',', '.') as stationen,
    replace(format('{:,}', coalesce(sum(lp_hpc + lp_schnell + lp_normal), 0)::bigint), ',', '.') as ladepunkte,
    replace(format('{:,}', coalesce(sum(lp_hpc), 0)::bigint), ',', '.') as hpc_ladepunkte,
    replace(format('{:.2f}', coalesce(sum(kw) filter (where matches), 0) / 1e6), '.', ',') || ' GW' as gesamtleistung,
    bool_or(sel_hpc or sel_schnell or sel_normal) as any_selected
from ${filtered}
```

```sql zubau
select jahr, sum(lp_hpc + lp_schnell + lp_normal) as ladepunkte
from ${filtered}
where jahr >= 2010
group by jahr
order by jahr
```

```sql zubau_typ
select jahr, kategorie, sum(ladepunkte) as ladepunkte
from (
    select jahr, 'HPC-Laden (>= 150 kW)' as kategorie, lp_hpc as ladepunkte from ${filtered} where sel_hpc
    union all
    select jahr, 'Schnellladen (> 22 kW)', lp_schnell from ${filtered} where sel_schnell
    union all
    select jahr, 'Normalladen (<= 22 kW)', lp_normal from ${filtered} where sel_normal
)
where jahr >= 2010
group by jahr, kategorie
order by jahr
```

{#if kpis[0].any_selected}

<Grid cols=4>
    <BigValue data={kpis} value=stationen title="Ladestationen"/>
    <BigValue data={kpis} value=ladepunkte title="Ladepunkte"/>
    <BigValue data={kpis} value=hpc_ladepunkte title="HPC-Ladepunkte"/>
    <BigValue data={kpis} value=gesamtleistung title="Gesamtleistung"/>
</Grid>

<Grid cols=2>
    <BarChart
        data={zubau}
        x=jahr
        y=ladepunkte
        xFmt="0"
        fillColor="#003247"
        title="Jährlicher Zubau von Ladepunkten (Gesamt)"
        yAxisTitle="Ladepunkte"
    />
    <BarChart
        data={zubau_typ}
        x=jahr
        y=ladepunkte
        xFmt="0"
        series=kategorie
        seriesOrder={['HPC-Laden (>= 150 kW)', 'Schnellladen (> 22 kW)', 'Normalladen (<= 22 kW)']}
        seriesColors={{'HPC-Laden (>= 150 kW)': '#00B092', 'Schnellladen (> 22 kW)': '#003247', 'Normalladen (<= 22 kW)': '#D3D3D3'}}
        title="Jährlicher Zubau nach Leistungstyp"
        yAxisTitle="Ladepunkte"
    />
</Grid>

{:else}

<Alert status="warning">Bitte wähle mindestens einen Leistungstyp aus.</Alert>

{/if}
