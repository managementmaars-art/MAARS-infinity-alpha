---
name: architecture-ai
description: AI architecture skills — design generation, BIM analysis, space planning, building code compliance, material specifications, 3D visualization prompts for MAARS architecture agents
---

# Architecture AI — MAARS Reference

## Architectural Design Assistant
```python
DESIGN_CONCEPT_PROMPT = """
Generate an architectural design concept.
Project type: {project_type}
Location: {location}
Climate zone: {climate}
Site area: {site_area} m²
Program: {program} (spaces required)
Budget: ${budget} per m²
Style direction: {style}
Client priorities: {priorities}
Sustainability target: {sustainability} (LEED Gold/BREEAM Excellent/Passive House)

Develop:
1. CONCEPT NARRATIVE (150 words): Core idea, inspiration, vision
2. DESIGN PRINCIPLES: 3-5 guiding principles
3. SPATIAL ORGANIZATION:
   - Primary circulation strategy
   - Public/private/service zone hierarchy
   - Indoor/outdoor relationship
4. BUILDING FORM:
   - Primary geometry rationale
   - Facade approach
   - Roof strategy
5. STRUCTURAL CONCEPT:
   - Primary structural system
   - Span strategies
   - Materials palette
6. ENVIRONMENTAL STRATEGY:
   - Passive design (orientation, shading, natural ventilation)
   - Energy systems
   - Water management
7. MATERIALITY:
   - Primary, secondary, accent materials
   - Tactile and visual rationale
8. KEY SPACES: Describe 3 most important spaces in detail
"""
```

## Space Planning Optimization
```python
SPACE_PLANNING_PROMPT = """
Optimize space planning for: {building_type}
Total area: {total_area} m²
Floors: {floors}
Occupancy: {occupancy} people

Program requirements:
{space_list}

Generate:
1. AREA SCHEDULE: Each space with target area and % of total
2. ADJACENCY MATRIX: Which spaces must/should/should not be adjacent
3. CIRCULATION EFFICIENCY:
   - Net/Gross ratio target: {target_ratio}%
   - Primary circulation width recommendations
   - Vertical circulation (stairs/lifts) requirements
4. ZONING STRATEGY: How to cluster spaces
5. FLEXIBILITY: Which spaces can multipurpose
6. CODE COMPLIANCE CHECKS:
   - Occupancy calculations per space
   - Exit distance requirements
   - Accessible path of travel

Building type benchmarks:
Office: 12-18 m² per person
Residential: 30-50 m² per bedroom
Retail: 3-8 m² per customer at peak
Hospitality: 25-50 m² per room (total GFA)
"""

SPACE_STANDARDS = {
    "office_workstations": {
        "open_plan": 8,    # m² per person (min)
        "standard": 12,    # m² per person
        "executive": 20,   # m² per person
    },
    "meeting_rooms": {
        "small_4_pax": 12,
        "medium_8_pax": 24,
        "large_12_pax": 40,
        "boardroom_20_pax": 70,
    },
    "residential_minimum_uk": {
        "studio": 37,
        "1_bed_1_person": 39,
        "1_bed_2_person": 50,
        "2_bed_3_person": 61,
        "2_bed_4_person": 70,
        "3_bed_5_person": 86,
    },
}
```

## Building Code Compliance
```python
COMPLIANCE_REVIEW_PROMPT = """
Review this design for building code compliance.
Jurisdiction: {jurisdiction}
Building type/use: {use_class}
Occupancy load: {occupancy}
Building height: {height}m
Construction type: {construction_type}

Check compliance with:
1. MEANS OF EGRESS:
   - Exit distances (travel to exit vs. code maximum)
   - Number of exits required
   - Exit width calculation
   - Stair requirements (width, rise, going)

2. ACCESSIBILITY (ADA/BS8300):
   - Accessible entrance
   - Lift requirement (if applicable)
   - Accessible WC provision
   - Ramp gradients

3. FIRE SAFETY:
   - Compartmentation
   - Fire rated construction requirements
   - Sprinkler requirement
   - Fire detection and alarm

4. STRUCTURAL (general):
   - Floor loading requirements by use
   - Wind load exposure category

5. PLANNING/ZONING:
   - Height limits
   - Setbacks
   - Coverage ratios
   - Parking requirements

Flag: COMPLIANT / NON-COMPLIANT / REQUIRES SPECIALIST REVIEW
"""
```

## Material Specification
```python
MATERIAL_SPEC_PROMPT = """
Generate material specifications for: {element}
Context: {building_type}, {location_environment}
Budget level: {budget} (value/standard/premium/luxury)
Sustainability requirement: {sustainability_level}
Lead time: {lead_time}

For each specification:
1. MATERIAL: Name and grade
2. MANUFACTURER: Recommended suppliers (3 options)
3. TECHNICAL SPEC:
   - Fire rating
   - Thermal performance (U-value/R-value)
   - Acoustic performance (if relevant)
   - Durability/life expectancy
4. FINISH SPECIFICATION: Color, texture, profile
5. INSTALLATION METHOD: Fixing system, substrate requirements
6. MAINTENANCE: Cleaning, recoating, inspection schedule
7. SUSTAINABILITY CREDENTIALS: Recycled content, EPD, certifications
8. COST ESTIMATE: $/m² supply + install
9. ALTERNATIVES: 2 value-engineered options
"""

MATERIAL_LIBRARY = {
    "cladding": {
        "premium": ["Zinc (Rheinzink)", "Copper patina", "Terracotta panels"],
        "standard": ["Composite aluminum", "Fiber cement", "Brick slip"],
        "value": ["Render", "Timber cladding", "Steel profiled sheet"],
    },
    "flooring": {
        "premium": ["Porcelain large format", "Natural stone", "Engineered oak"],
        "standard": ["Polished concrete", "LVT", "Carpet tiles (Interface)"],
        "value": ["Vinyl sheet", "Laminate", "Polished screed"],
    },
    "structure": {
        "concrete": {"co2_per_tonne": 410, "life": 100},
        "steel": {"co2_per_tonne": 1850, "life": 75},
        "mass_timber": {"co2_per_tonne": -1800, "life": 60},  # carbon stored
        "timber_frame": {"co2_per_tonne": -900, "life": 60},
    },
}
```

## Visualization & Rendering Prompts
```python
ARCHITECTURAL_VIZ_PROMPTS = {
    "exterior_hero": """
Architectural visualization of a {building_type}, {style} architecture.
{material_description}. Photographed from eye-level perspective,
golden hour lighting, dramatic sky with clouds. Context: {setting}.
Photorealistic, 8K resolution, architectural photography style,
professional CGI rendering. No people.
""",
    "interior_living": """
Interior architectural photography of a {room_type}, {style} design.
Materials: {materials}. Natural light from {window_direction},
warm afternoon sun, casting long shadows. {furniture_style} furniture.
Architectural Digest quality, wide-angle lens, immaculate composition.
""",
    "aerial_masterplan": """
Aerial drone view of {development_name}, master planned development.
{landscape_description}. Multiple buildings arranged {layout_description}.
Professional architectural aerial photography, blue sky,
lush landscaping, people to scale.
""",
}

def generate_architectural_image(prompt_type: str, params: dict) -> str:
    """Generate architectural visualization"""
    import anthropic
    # Use image generation API
    template = ARCHITECTURAL_VIZ_PROMPTS[prompt_type]
    prompt = template.format(**params)
    # → Send to DALL-E 3, Midjourney API, or Stability AI
    return prompt
```

## BIM Data Extraction
```python
# IFC (BIM) file parsing
import ifcopenshell

def analyze_bim_model(ifc_path: str) -> dict:
    model = ifcopenshell.open(ifc_path)
    
    # Count elements by type
    walls = model.by_type("IfcWall")
    slabs = model.by_type("IfcSlab")
    spaces = model.by_type("IfcSpace")
    doors = model.by_type("IfcDoor")
    windows = model.by_type("IfcWindow")
    
    # Calculate areas
    total_floor_area = sum(
        s.get_info().get("GrossFloorArea", 0) for s in spaces
    )
    
    # Extract materials
    materials = set()
    for element in model.by_type("IfcElement"):
        for assoc in element.HasAssociations:
            if assoc.is_a("IfcRelAssociatesMaterial"):
                materials.add(str(assoc.RelatingMaterial))
    
    return {
        "element_count": {
            "walls": len(walls), "slabs": len(slabs),
            "spaces": len(spaces), "doors": len(doors), "windows": len(windows),
        },
        "total_floor_area_m2": total_floor_area,
        "materials_used": list(materials)[:20],
        "model_status": "Loaded successfully",
    }
```

## Models to Use
- **Design concepts**: `claude-opus-4-6` (creative + technical synthesis)
- **Code compliance review**: `claude-opus-4-6` (precision, safety-critical)
- **Space planning**: `claude-sonnet-4-6` (systematic optimization)
- **Material research**: `perplexity/sonar-pro` (current products + pricing)
- **Visualization prompts**: `claude-sonnet-4-6` → DALL-E 3 or Midjourney
- **BIM analysis**: `gpt-4o` with code tools (data parsing)
- **Specification writing**: `claude-sonnet-4-6` (technical prose)
