# Rail material comparison

Options from `docs/portfolio/rail-design-review.pdf`, plus aluminum extrusion. Values marked † are not yet sourced.

## Options

| # | Option | Carriage |
| --- | --- | --- |
| A | Clear acrylic sheet, laser-cut, heat-bent | Custom |
| B | 3D-printed PLA, doweled sections | Custom |
| C | Sasco S2 SL2-G 120 strut, 12 ga, pre-galvanized | Sasco S875T-EG trolley |
| D | 2040 V-slot aluminum extrusion, 6063-T5, anodized | V-slot gantry plate, POM V-wheels |

## Data

| Property | A Acrylic | B PLA | C Sasco S2, 12 ga | D 2040 V-slot |
| --- | --- | --- | --- | --- |
| Tensile strength | 65 MPa [1] | 50–60 MPa [2] | 400–841 MPa (galvanized) [3] | — |
| Flexural strength | 90 MPa [1] | — | — | — |
| Elastic modulus E | ~3 GPa † | ~3.5 GPa † | ~200 GPa † | 68.9 GPa [4] |
| Mass per metre | — | — | 2.81 kg/m [5] | 0.799 kg/m [6] |
| Cross-section area | — | — | 3.60 cm² [5] | 2.96 cm² [6] |
| Second moment of area | — | — | 7.74 cm⁴ (x), 9.66 cm⁴ (y) [5] | 4.75 cm⁴ (stiff), 1.21 cm⁴ (weak) [6] |
| Corrosion | — | — | Pre-galvanized G90 [5]; cut ends bare steel † | Anodized [6] |
| Carriage rating | — | — | S875T-EG: 100 lb (0.44 kN), no speed rating; rated Sasco trolleys listed to 180 ft/min (0.91 m/s) [7] | — |
| Cost | $98 (0.08 in) / $138 (0.118 in) per 24×48 in sheet, plus laser cutting [8] | ~$30/roll, 3–4 rolls = $90–120 [9] | ~$0, team member surplus [8] | CAD $0.29/cm or CAD $34.89 per 200 cm, plus CAD $2.99 per custom cut [10]; gantry plate + 6 POM wheels CAD $3.49–9.79 [11] |
| Actuator force, slide 5 | 14.65 N (labelled "Sasco Strut", likely acrylic) | 14.95 N | 25.78 N | Not computed; rail mass 0.96 kg at 1.2 m |

Strut properties are for solid S2. The review specifies slotted SL2, which is lighter and less stiff. Cross-check for D: Misumi HFS5-2040 (T-slot, not V-slot) lists 0.88 kg/m, 3.24 cm², 5.13 / 1.358 cm⁴ [12].

### Deflection check

30 N (3 kg aircraft, slide 5) at mid-span of a 1.2 m rail, simply supported. δ = FL³ / (48EI).

| Rail | EI (N·m²) | δ |
| --- | --- | --- |
| C Sasco S2, x-axis | 15,480 † | 0.07 mm |
| D 2040, stiff axis (40 mm vertical) | 3,273 | 0.33 mm |
| D 2040, weak axis (laid flat) | 834 | 1.30 mm |

Mount 2040 with the 40 mm side vertical.

### Aluminum cost, two 1.2 m rails

| Item | CAD |
| --- | --- |
| 2 × 120 cm at $0.29/cm | 69.60 |
| 2 custom-cut fees at $2.99 | 5.98 |
| 2 gantry plates, upper price | 19.58 |
| Total before tax and shipping | 95.16 |

## Suppliers and datasheets

| Option | Supplier | Datasheet |
| --- | --- | --- |
| D | [diycnc.ca, 2040 V Slot Aluminum Profile](https://diycnc.ca/product/2040-v-slot-aluminum-profile/). Custom lengths need a registered account; 200 cm max standard. | [Systéal V-SLOT 20×40](https://www.systeal.com/en/profiles-20-series/1226-v-slot-aluminium-profile-20x40-6mm-slot.html) |
| D | [diycnc.ca, Motion System](https://diycnc.ca/product-category/3d-printer-parts/motion-system/) (gantry plates) | [OpenBuilds deflection guide](https://naylampmechatronics.com/img/cms/V-Slot/How%20to%20Estimate%20Deflection%20in%20Your%20Open%20Builds%20Projects_v2.pdf) |
| C | Team member surplus | [Sasco catalogue](https://old.sascostrut.com/application/files/5916/4986/4782/Catalogue_2.21_-_Web.pdf), [Sasco trolleys](https://old.sascostrut.com/product-catalogue/fittings/general-fittings/trolleys) |

The diycnc profile is unbranded and lists only the alloy. Weigh a cut piece against 0.799 kg/m to confirm it matches the datasheet geometry.

## Unsourced (†)

- E for acrylic, PLA, steel.
- Bare steel at cut ends of pre-galvanized strut.

## Weighted decision matrix

Scores: 1 = worst, 5 = best. Weights sum to 100.

### Criteria

| Criterion | Weight | Basis |
| --- | --- | --- |
| Stiffness | 20 | E and second moment of area; deflection check |
| Impact toughness at brake stop | 15 | Brittle plastics; PLA layer seams |
| Carriage fit | 15 | Ready-made carriage; adjustable play; rating |
| Corrosion in spray | 10 | Coating; exposed cut ends |
| Mass | 10 | Mass per metre; actuator force, slide 5 |
| Cost to $500 fund | 10 | Data table |
| Fabrication effort and error risk | 10 | Review fabrication notes |
| Mounting modularity | 10 | Bolting brake stop, latch, IMU, actuator, boat clamps without drilling |

### Scores

| Criterion | Weight | A Acrylic | B PLA | C Strut | D 2040 V-slot |
| --- | --- | --- | --- | --- | --- |
| Stiffness | 20 | 1 | 1 | 5 | 4 |
| Impact toughness | 15 | 1 | 1 | 5 | 4 |
| Carriage fit | 15 | 2 | 2 | 3 | 5 |
| Corrosion | 10 | 5 | 4 | 2 | 4 |
| Mass | 10 | 5 | 5 | 1 | 4 |
| Cost | 10 | 2 | 3 | 5 | 3 |
| Fabrication | 10 | 1 | 3 | 4 | 5 |
| Modularity | 10 | 1 | 2 | 4 | 5 |
| **Weighted total (out of 5)** | 100 | **2.05** | **2.35** | **3.80** | **4.25** |

Weighted total = Σ(weight × score) / 100.

Ranking: D, C, B, A. C passes D only if the cost weight rises above 32.5 with the other weights unchanged.

## References

1. McNeall Plastics, "Everything about acrylic plastics." https://www.mcneallplastics.com.au/news/everything-about-acrylic-plastics
2. Formlabs, "Strongest 3D printing materials." https://formlabs.com/blog/strongest-3d-printing-materials/
3. Unified Alloys, "Stainless steel vs galvanized." https://www.unifiedalloys.com/blog/stainless-steel-vs-galvanized/
4. OpenBuilds, "How to Estimate Deflection in Your Open Builds Projects." https://naylampmechatronics.com/img/cms/V-Slot/How%20to%20Estimate%20Deflection%20in%20Your%20Open%20Builds%20Projects_v2.pdf
5. Sasco Strut, General Catalogue 2.21, "Elements of Sasco Steel Channels" (metric). https://old.sascostrut.com/application/files/5916/4986/4782/Catalogue_2.21_-_Web.pdf
6. Systéal, "V-SLOT Aluminium profile 20x40 6mm slot," data sheet. https://www.systeal.com/en/profiles-20-series/1226-v-slot-aluminium-profile-20x40-6mm-slot.html
7. Sasco Strut, "Trolleys." https://old.sascostrut.com/product-catalogue/fittings/general-fittings/trolleys
8. `docs/portfolio/rail-design-review.pdf`; Home Depot Canada, acrylic sheets. https://www.homedepot.ca/en/home/categories/building-materials/plexiglass-and-acrylic-sheets.html
9. Qkits, 1.75 mm PLA filament, 1 kg. https://store.qkits.com/1-75mm-pla-filament-translucent-1-kg.html
10. DIY CNC Canada, "2040 V Slot Aluminum Profile." https://diycnc.ca/product/2040-v-slot-aluminum-profile/ and "Custom Length Items Ordering." https://diycnc.ca/order-custom-length/
11. DIY CNC Canada, "Motion System." https://diycnc.ca/product-category/3d-printer-parts/motion-system/
12. MISUMI, "Aluminum Extrusions (HFS5 Series)." https://us.misumi-ec.com/pdf/fa/2019/2019_US_2686.pdf
