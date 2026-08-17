# ZEON Benchmark Results

> Generated automatically. Tokenizer: `cl100k_base` (GPT-4 / tiktoken)

## Token Efficiency Summary

| Dataset | Tabular | JSON (compact) | YAML | **ZEON** | vs JSON | vs YAML |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| Employee Records (100, uniform flat) | 100% | 2,804 | 3,702 | **1,709** | `-39.1%` | `-53.8%` |
| E-commerce Orders (50, nested) | 33% | 4,933 | 6,220 | **3,581** | `-27.4%` | `-42.4%` |
| Time-series Analytics (60, uniform flat) | 100% | 2,332 | 2,870 | **1,498** | `-35.8%` | `-47.8%` |
| GitHub Repositories (30, uniform flat) | 100% | 2,083 | 2,461 | **1,188** | `-43.0%` | `-51.7%` |
| Contacts with Address (50, nested) | 100% | 2,603 | 3,302 | **1,716** | `-34.1%` | `-48.0%` |
| Feature Flags (40, keyed map) | 100% | 825 | 963 | **487** | `-41.0%` | `-49.4%` |
| Semi-uniform Event Logs (75, mixed) | 50% | 2,944 | 3,617 | **2,303** | `-21.8%` | `-36.3%` |
| Deeply Nested Config (1, deep) | 0% | 137 | 173 | **105** | `-23.4%` | `-39.3%` |

**TOTAL** | | 18,661 | 23,308 | **12,587** | `-32.5%` | `-46.0%`


## Detailed Token Counts per Dataset

### Employee Records (100, uniform flat)
> Tabular eligibility: 100%

```
ZEON         ####................     1709 tokens
JSON compact ######..............     2804 tokens  (-39.1% vs ZEON)
YAML         ########............     3702 tokens  (-53.8% vs ZEON)
```

### E-commerce Orders (50, nested)
> Tabular eligibility: 33%

```
ZEON         ########............     3581 tokens
JSON compact ###########.........     4933 tokens  (-27.4% vs ZEON)
YAML         ##############......     6220 tokens  (-42.4% vs ZEON)
```

### Time-series Analytics (60, uniform flat)
> Tabular eligibility: 100%

```
ZEON         ###.................     1498 tokens
JSON compact #####...............     2332 tokens  (-35.8% vs ZEON)
YAML         ######..............     2870 tokens  (-47.8% vs ZEON)
```

### GitHub Repositories (30, uniform flat)
> Tabular eligibility: 100%

```
ZEON         ##..................     1188 tokens
JSON compact ####................     2083 tokens  (-43.0% vs ZEON)
YAML         #####...............     2461 tokens  (-51.7% vs ZEON)
```

### Contacts with Address (50, nested)
> Tabular eligibility: 100%

```
ZEON         ####................     1716 tokens
JSON compact ######..............     2603 tokens  (-34.1% vs ZEON)
YAML         #######.............     3302 tokens  (-48.0% vs ZEON)
```

### Feature Flags (40, keyed map)
> Tabular eligibility: 100%

```
ZEON         #...................      487 tokens
JSON compact #...................      825 tokens  (-41.0% vs ZEON)
YAML         ##..................      963 tokens  (-49.4% vs ZEON)
```

### Semi-uniform Event Logs (75, mixed)
> Tabular eligibility: 50%

```
ZEON         #####...............     2303 tokens
JSON compact #######.............     2944 tokens  (-21.8% vs ZEON)
YAML         ########............     3617 tokens  (-36.3% vs ZEON)
```

### Deeply Nested Config (1, deep)
> Tabular eligibility: 0%

```
ZEON         ....................      105 tokens
JSON compact ....................      137 tokens  (-23.4% vs ZEON)
YAML         ....................      173 tokens  (-39.3% vs ZEON)
```
