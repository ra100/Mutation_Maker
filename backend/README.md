# Backend code customization

This README contains instructions for developers how to customize the Mutation Maker backend code in order to allow for changing the hardcoded parameters and default values.

More advanced users can modify these parameters to better optimize the Mutation Maker calculations for their specific reaction conditions.

## Melting temperature calculation


The primer melting temperature `Tm` is calculated using the Primer3-py Python package: 
- Primer3-py source: https://github.com/libnano/primer3-py
- Primer3-py documentation: https://libnano.github.io/primer3-py/index.html

It can be found in the [mutation_maker.temperature_calculator](mutation_maker/temperature_calculator.py) module.

The melting temperature calculation uses the nearest neighbors Santa Lucia approach and the following default settings: 

```
calculation_method = "santalucia"
salt_correction = "owczarzy"
na = 50 (Na+ ion concentrations, mM)
k = 50 (K+ ion concentration, mM)
tris = 20 (Tris-HCL concentration, mM)
mg = 2 (Mg2+ ion concentration, mM)
dntp = 0.2 (dNTP concentration, mM)
dnac1 = 500 (primer concentration, for PAS was set to simulated concentration of 583 nmM)
precision = 1 (precision of the temperature calculation in digits after the decimal point)
```

For PAS oligo Tm’s a Tm correction factor of 3 °C was applied.

The buffer conditions are set to support Q5 reactions. However, the minimum and maximum reaction Tm is fully adjustable, so users that know their Tm range can set the optimal parameters to reflect their reaction conditions.


### Changing Tm calculation parameters

There's a class `TemperatureConfig` that can be instantiated with different values of the abovementioned parameters.

```
TemperatureConfig(
    calculation_type = StringProperty(required=True, choices=["Wallace", "GC", "NN", "NEB_like"], default="NN")
    gc_value_set = StringProperty(choices=gc_value_sets, default="QuickChange")
    nn_table = StringProperty(choices=nn_tables, default="SantaLucia_1997")
    salt_correction = StringProperty(choices=salt_corrections, default="Owczarzy_2004")
    dnac1 = FloatProperty(default=500)
    dnac2 = FloatProperty(default=25)
    na = FloatProperty(default=50)
    k = FloatProperty(default=50)
    tris = FloatProperty(default=20)
    mg = FloatProperty(default=2)
    dntp = FloatProperty(default=0.2)
    precision = IntegerProperty(default=0)
)
```

### Allowed paramater values:

Th following section describes the range of available values for some of the parameters above.

GC value sets:
```
gc_value_sets = ["Chester_1993", "QuickChange", "Schildkraut_1965", "Wetmur_Melting_1991","Wetmur_RNA_1991", "Wetmur_DNA_RNA_1991", "Primer3", "Ahsen_2001"]
```

NN tables:
```
nn_tables = ["SantaLucia_1997", "SantaLucia_2004", "Breselauer_1986", "Sugimoto_1996"]
```

Salt corrections:
```
salt_corrections = ["No", "Schildkraut_1965", "Wetmur_1991", "SantaLucia_1996", "SantaLucia_1998","SantaLucia_DeltaS_1998", "Owczarzy_2004", "Owczarzy_2008"]
```
