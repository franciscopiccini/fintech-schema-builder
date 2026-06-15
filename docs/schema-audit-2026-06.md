# Auditoría de schemas — fintech-schema-builder

**Fecha:** 2026-06-14
**Vocabulario de referencia:** [schema.org v30.0](https://schema.org/version/30.0/) (`schemaorg-current-https.jsonld`)
**Alcance:** revisión de los 9 builders en [src/schema_automation/schema/](../src/schema_automation/schema/) contra las propiedades disponibles en el vocabulario oficial.

---

## Resumen ejecutivo

| Builder | Props usadas / disponibles | Estado |
|---|---|---|
| `PaymentCard` | 8/46 (17%) | 🔴 Faltan props críticas (interestRate, APR) |
| `LoanOrCredit` | 15/50 (30%) | 🟡 Falta loanType y específicas de préstamos |
| `BankAccount` | 14/44 (32%) | 🟡 Falta `bankAccountType` (diferenciador clave) |
| `PaymentService` | 9/42 (21%) | 🟡 Falta canales y horarios |
| `FinancialProduct` | 12/41 (29%) | 🟡 Falta marca + identificación |
| `InvestmentOrDeposit` | 9/42 (21%) | 🔴 Sin interestRate / APR |
| `InsuranceAgency` | 11/128 (9%) | 🔴 LocalBusiness sin contacto ni horarios |
| `BlogPosting` | 9/137 (7%) | 🟡 SEO editorial muy desaprovechado |
| `Event` | 11/56 (20%) | 🟡 Falta segmentación + sponsors |

---

## Hallazgos transversales

Aplican a **todos** los builders salvo aclaración:

### 1. `brand` ausente en productos
Ningún builder declara `brand`. Google lo usa en rich results de productos financieros.
**Fix:** `"brand": {"@type": "Brand", "name": "Naranja X"}` o referencia `@id` a la Organization.

### 2. `sameAs` ausente
Productos y Organization no enlazan a perfiles oficiales (LinkedIn, Instagram, Facebook, Wikipedia). `sameAs` consolida el entity graph en Google Knowledge Graph.

### 3. `identifier` ausente en productos
PaymentCard y LoanOrCredit no llevan identificador (SKU interno, código de producto). Útil para tracking en Search Console y disambiguación cuando hay variantes.

### 4. `review` (individual) ausente
Solo se emite `aggregateRating`. Agregar `review` con `Review` reales (Trustpilot, Google Reviews) refuerza E-E-A-T.

### 5. `termsOfService` / `feesAndCommissionsSpecification`
Especialmente en `PaymentCard` y `LoanOrCredit`: schema.org acepta URL al T&C o spec de comisiones. **Crítico** para productos financieros regulados (BCRA).

### 6. `potentialAction` ausente
Sin `potentialAction` (ej. `ApplyAction` para préstamos/tarjetas, `OrderAction` para seguros) se pierde la señal de conversión. Google la usa para action snippets.

### 7. `audience` ausente
Naranja X tiene productos segmentados (monotributistas, jubilados, viajeros). `audience: {"@type": "PeopleAudience", "audienceType": "Monotributistas"}` mejora relevancia semántica.

---

## Hallazgos por builder

### PaymentCard
[src/schema_automation/schema/payment_card.py](../src/schema_automation/schema/payment_card.py) — Usa 8/46 props.

**Faltantes críticas:**
- **`annualPercentageRate`** y **`interestRate`** — obligatorios en comunicación de tarjetas de crédito (CFT, TNA)
- `feesAndCommissionsSpecification` — comisión por renovación, costo de mantenimiento
- `termsOfService`, `category` ("credit_card"), `brand`

---

### LoanOrCredit
[src/schema_automation/schema/loan_or_credit.py](../src/schema_automation/schema/loan_or_credit.py) — Usa 15/50 props.

**Faltantes específicas de préstamos:**
- **`loanType`** — "personal", "express", "viaje" (matchea con tu catálogo `prestamos` en [config.py](../src/schema_automation/config.py))
- **`gracePeriod`** — período de gracia
- **`requiredCollateral`** — garantías exigidas
- **`recourseLoan`** (bool), **`renegotiableLoan`** (bool)
- `feesAndCommissionsSpecification`, `termsOfService`

---

### BankAccount
[src/schema_automation/schema/bank_account.py](../src/schema_automation/schema/bank_account.py) — Usa 14/44 props.

**Faltantes críticas:**
- **`bankAccountType`** — "savings", "checking", "Cuenta Remunerada". Es el diferenciador clave entre Caja de Ahorro, Cuenta en Dólares y Cuenta Remunerada (hoy los tres usan el mismo `@type` y solo cambian en el `name`).
- `termsOfService`, `category`

---

### PaymentService
[src/schema_automation/schema/payment_service.py](../src/schema_automation/schema/payment_service.py) — Usa 9/42 props.

**Faltantes:**
- `availableChannel` — canales (app, web, presencial)
- `hoursAvailable` — disponibilidad 24/7
- `aggregateRating`, `termsOfService`

---

### InvestmentOrDeposit
[src/schema_automation/schema/investment_or_deposit.py](../src/schema_automation/schema/investment_or_deposit.py) — Usa 9/42 props.

**Faltantes críticas:**
- **`interestRate`**, **`annualPercentageRate`** — sin esto el schema de un plazo fijo o Cuenta Remunerada es inservible
- `feesAndCommissionsSpecification`, `aggregateRating`

---

### InsuranceAgency
[src/schema_automation/schema/insurance_agency.py](../src/schema_automation/schema/insurance_agency.py) — Usa 11/128 props.

**Faltantes (heredadas de `LocalBusiness`):**
- **`telephone`**, **`email`** — datos de contacto obligatorios para LocalBusiness según guidelines de Google
- **`openingHoursSpecification`** — horarios de atención
- `slogan`, `keywords`

---

### BlogPosting
[src/schema_automation/schema/blog_posting.py](../src/schema_automation/schema/blog_posting.py) — Usa 9/137 props.

**Faltantes de alto impacto SEO editorial:**
- **`articleBody`** — contenido completo del artículo
- **`articleSection`** — categoría del blog (Finanzas Personales, Educación Financiera, etc.)
- **`wordCount`**, **`inLanguage`** ("es-AR"), **`keywords`**
- **`speakable`** — Google Assistant / búsquedas por voz
- `author` debería ser `Person` con `url` y `sameAs`, no solo `name`

---

### Event
[src/schema_automation/schema/event.py](../src/schema_automation/schema/event.py) — Usa 11/56 props.

**Faltantes para Hot Sale / CyberMonday:**
- **`previousStartDate`** — útil si reschedulan
- **`maximumAttendeeCapacity`**, **`subEvent`** (sub-promociones por categoría), **`performer`**, **`sponsor`**
- `keywords` ("Hot Sale 2026", "CyberMonday")

---

### Offer (compartido entre builders)
Usa 11/67 props en todos los builders.

**Faltantes en contexto fintech:**
- **`eligibleCustomerType`** — `"Business"` (monotributista) vs `"Consumer"`
- **`eligibleDuration`** — duración de la elegibilidad
- **`itemCondition`** — `NewCondition` (default esperado por Google)
- **`hasMerchantReturnPolicy`** — Google lo exige cada vez más

---

### Product (envoltorios)
Usa 6/72 props. Faltan: `brand`, `sku`, `gtin13`, `category`, `itemCondition`, `audience`.

---

### FAQPage
Usa 2/139 props. Considerar:
- **`inLanguage`** ("es-AR")
- **`speakable`** — voice search

---

## Bugs semánticos detectados

1. **`price: "0"` en PaymentCard** — semánticamente incorrecto. Una tarjeta de crédito no tiene "precio cero", tiene costo de emisión y/o mantenimiento. Opciones:
   - Reemplazar por `PriceSpecification` con la comisión real
   - Eliminar `offers` si el producto se promociona sin precio de emisión

2. **`availability: InStock`** en productos financieros — `InStock` es de e-commerce físico. Para servicios financieros revisar si corresponde o eliminarlo.

3. **`provider` como array `[…]` en PaymentCard** pero como `dict {…}` en BankAccount — inconsistencia entre builders.

4. **IDs sin convención unificada:**
   - `#PaymentCard` (PascalCase)
   - `#bankaccount` (minúscula)
   - `#producto` (español)
   Estandarizar a PascalCase coincidiendo con `@type`.

5. **`mainEntityOfPage` apunta a `#WebPage`** pero el WebPage node se appendea al final del grafo — verificar que siempre exista antes de las referencias.

6. **`VALID_SCHEMA_TYPES` hardcoded** en [validation/validator.py](../src/schema_automation/validation/validator.py) — desincronizado del vocab real. Considerar reemplazar por validación contra `schemaorg-current-https.jsonld` (disponible en el fork local en `~/Desktop/Tooling/schemaorg/`).

---

## Roadmap priorizado

| Prioridad | Cambio | Impacto | Esfuerzo |
|---|---|---|---|
| 🔴 P0 | `brand` + `sameAs` en todos los productos | Entity graph / KG | Bajo |
| 🔴 P0 | `interestRate` / `annualPercentageRate` en PaymentCard e InvestmentOrDeposit | Compliance + rich results | Medio (requiere datos) |
| 🔴 P0 | `bankAccountType` en BankAccount + `loanType` en LoanOrCredit | Diferenciación de productos | Bajo |
| 🔴 P0 | Bugs semánticos #1–4 | Calidad del JSON-LD | Bajo |
| 🟡 P1 | `telephone` + `email` + `openingHoursSpecification` en InsuranceAgency | LocalBusiness requirements | Bajo |
| 🟡 P1 | `articleBody`, `articleSection`, `inLanguage`, `wordCount` en BlogPosting | SEO editorial | Medio (parsing) |
| 🟡 P1 | `potentialAction` (ApplyAction) en productos crediticios | Action snippets | Medio |
| 🟡 P1 | `feesAndCommissionsSpecification` (URL al T&C) | Productos regulados | Bajo |
| 🟢 P2 | `audience` segmentado por catálogo | Relevancia semántica | Bajo |
| 🟢 P2 | `speakable` en BlogPosting y FAQPage | Voice search | Bajo |
| 🟢 P2 | `itemCondition: NewCondition` en todos los Offer | Validación Google estricta | Bajo |
| 🟢 P2 | Validator dinámico contra schema.org JSON-LD | Mantenibilidad | Alto |

---

## Próximos pasos sugeridos

1. Atacar P0 en un PR único (cambios mecánicos en `base.py` + builders puntuales)
2. P1 en PRs separados por builder (cambios con lógica de extracción nueva)
3. P2 como work backlog conforme se identifiquen casos puntuales
