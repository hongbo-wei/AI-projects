"""
Advertising Tools for MCP Server
Implements budget calculator, effect analyzer, and compliance checker tools.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from mcp import Tool


class BudgetCalculatorInput(BaseModel):
    """Input model for budget calculator tool."""
    budget: float = Field(..., description="Total advertising budget in USD")
    platforms: List[str] = Field(..., description="List of platforms to advertise on")
    region: str = Field(..., description="Target region (e.g., 'southeast_asia')")
    duration_days: int = Field(..., description="Campaign duration in days")


class BudgetCalculatorOutput(BaseModel):
    """Output model for budget calculator tool."""
    platform_allocation: Dict[str, float]
    daily_spend: Dict[str, float]
    total_estimated_reach: int
    recommendations: List[str]


def budget_calculator_tool(
    budget: float,
    platforms: List[str],
    region: str,
    duration_days: int
) -> BudgetCalculatorOutput:
    """Calculate optimal budget allocation for advertising campaigns."""
    # Simple allocation logic - in real implementation, use ML models or APIs
    total_budget = budget
    platforms_list = platforms
    region_param = region
    duration = duration_days

    # Platform-specific multipliers (simplified)
    platform_multipliers = {
        "tiktok": 1.2,
        "facebook": 1.0,
        "instagram": 1.1,
        "google": 0.9
    }

    # Calculate allocations
    allocations = {}
    total_weight = sum(platform_multipliers.get(p, 1.0) for p in platforms_list)

    for platform in platforms_list:
        weight = platform_multipliers.get(platform, 1.0)
        allocation = (weight / total_weight) * total_budget
        allocations[platform] = round(allocation, 2)

    # Daily spend
    daily_spend = {p: round(alloc / duration, 2) for p, alloc in allocations.items()}

    # Estimated reach (simplified calculation)
    reach_multipliers = {
        "tiktok": 5000,
        "facebook": 3000,
        "instagram": 4000,
        "google": 2000
    }
    total_reach = sum(reach_multipliers.get(p, 1000) * alloc for p, alloc in allocations.items())

    # Recommendations
    recommendations = []
    if region_param == "southeast_asia" and "tiktok" in platforms_list:
        recommendations.append("TikTok has high engagement in Southeast Asia - consider increasing allocation")
    if duration < 7:
        recommendations.append("Campaign duration is short - focus on high-impact platforms")

    return BudgetCalculatorOutput(
        platform_allocation=allocations,
        daily_spend=daily_spend,
        total_estimated_reach=int(total_reach),
        recommendations=recommendations
    )


class EffectAnalyzerInput(BaseModel):
    """Input model for effect analyzer tool."""
    platform: str = Field(..., description="Platform to analyze")
    budget: float = Field(..., description="Budget allocated to this platform")
    target_audience: str = Field(..., description="Target audience description")
    campaign_type: str = Field(..., description="Type of campaign (awareness, conversion, etc.)")


class EffectAnalyzerOutput(BaseModel):
    """Output model for effect analyzer tool."""
    estimated_impressions: int
    estimated_clicks: int
    estimated_conversions: int
    ctr_prediction: float
    cpc_prediction: float
    roi_estimate: float
    insights: List[str]


def effect_analyzer_tool(
    platform: str,
    budget: float,
    target_audience: str,
    campaign_type: str
) -> EffectAnalyzerOutput:
    """Analyze expected performance metrics for advertising campaigns."""
    platform_param = platform
    budget_param = budget
    audience = target_audience
    campaign_type_param = campaign_type

    # Platform-specific performance metrics (simplified)
    platform_metrics = {
        "tiktok": {"ctr": 0.025, "cpc": 0.5, "conversion_rate": 0.03},
        "facebook": {"ctr": 0.015, "cpc": 0.8, "conversion_rate": 0.025},
        "instagram": {"ctr": 0.02, "cpc": 0.6, "conversion_rate": 0.028},
        "google": {"ctr": 0.03, "cpc": 0.4, "conversion_rate": 0.035}
    }

    metrics = platform_metrics.get(platform_param, {"ctr": 0.02, "cpc": 0.5, "conversion_rate": 0.03})

    # Calculate predictions
    estimated_clicks = int(budget_param / metrics["cpc"])
    estimated_impressions = int(estimated_clicks / metrics["ctr"])
    estimated_conversions = int(estimated_clicks * metrics["conversion_rate"])

    # ROI estimate (simplified)
    avg_conversion_value = 50  # Assume $50 average order value
    roi = (estimated_conversions * avg_conversion_value) / budget_param

    # Insights
    insights = []
    if platform_param == "tiktok" and "young" in audience.lower():
        insights.append("TikTok performs well with younger audiences")
    if campaign_type_param == "awareness":
        insights.append("For awareness campaigns, focus on impressions over conversions")
    if roi < 1.5:
        insights.append("Consider optimizing targeting or creative for better ROI")

    return EffectAnalyzerOutput(
        estimated_impressions=estimated_impressions,
        estimated_clicks=estimated_clicks,
        estimated_conversions=estimated_conversions,
        ctr_prediction=metrics["ctr"],
        cpc_prediction=metrics["cpc"],
        roi_estimate=round(roi, 2),
        insights=insights
    )


class ComplianceCheckerInput(BaseModel):
    """Input model for compliance checker tool."""
    platform: str = Field(..., description="Platform for compliance check")
    region: str = Field(..., description="Target region")
    ad_content: str = Field(..., description="Ad content to check")
    target_audience: str = Field(..., description="Target audience description")


class ComplianceCheckerOutput(BaseModel):
    """Output model for compliance checker tool."""
    compliant: bool
    issues: List[str]
    recommendations: List[str]
    risk_level: str


def compliance_checker_tool(
    platform: str,
    region: str,
    ad_content: str,
    target_audience: str
) -> ComplianceCheckerOutput:
    """Check advertising content compliance with regional regulations."""
    platform_param = platform
    region_param = region
    content = ad_content.lower()
    audience = target_audience.lower()

    issues = []
    recommendations = []

    # Regional compliance checks (simplified)
    if region_param == "europe":
        if "free" in content and "shipping" in content:
            issues.append("EU regulations require clear terms for 'free' offers")
            recommendations.append("Add clear terms and conditions for free shipping")
        if "children" in audience:
            issues.append("Stricter regulations for ads targeting children in EU")
            recommendations.append("Consult local regulations for child-targeted advertising")

    elif region_param == "asia":
        if "alcohol" in content:
            issues.append("Alcohol advertising restrictions vary by Asian country")
            recommendations.append("Check specific country regulations for alcohol ads")

    # Platform-specific checks
    if platform_param == "tiktok":
        if len(content) > 2200:
            issues.append("TikTok caption limit is 2200 characters")
            recommendations.append("Shorten caption to fit platform limits")

    # General checks
    if "guarantee" in content and "money back" in content:
        recommendations.append("Ensure money-back guarantee terms are clearly stated")

    compliant = len(issues) == 0
    risk_level = "low" if compliant else ("medium" if len(issues) <= 2 else "high")

    return ComplianceCheckerOutput(
        compliant=compliant,
        issues=issues,
        recommendations=recommendations,
        risk_level=risk_level
    )


# --------------------------
# Visual Autoregressive Modeling (VAR) tool (stub)
# --------------------------
class VARImageInput(BaseModel):
    """Input model for VAR image generator."""
    prompt: str = Field(..., description="Text prompt describing the desired ad image")
    width: int = Field(1024, description="Image width in pixels")
    height: int = Field(1024, description="Image height in pixels")
    style: Optional[str] = Field(None, description="Optional visual style (e.g., 'photorealistic', 'illustration')")


class VARImageOutput(BaseModel):
    """Output model for VAR image generator."""
    image_data_url: str
    mime_type: str
    metadata: Dict[str, Any]


def var_image_tool(prompt: str, width: int = 1024, height: int = 1024, style: Optional[str] = None) -> VARImageOutput:
    """Generate an advertising image from a prompt.

    NOTE: This is a minimal stub implementation that returns a simple SVG data URL as a placeholder so
    the tool can be used end-to-end without additional heavy image-generation dependencies. Replace
    this with a real VAR/modelscope/StableDiffusion implementation when ready.
    """
    # Create a simple SVG placeholder (no external deps)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n  <rect width="100%" height="100%" fill="#f3f4f6"/>\n  <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-size="36" fill="#111">Ad Image Placeholder</text>\n  <text x="50%" y="60%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#444">{prompt}</text>\n</svg>'''
    data_url = "data:image/svg+xml;utf8," + svg.replace('\n', '')

    metadata = {
        "width": width,
        "height": height,
        "style": style or "placeholder",
        "generator": "var_stub"
    }

    return VARImageOutput(image_data_url=data_url, mime_type="image/svg+xml", metadata=metadata)


# Tool definitions for MCP
BUDGET_CALCULATOR_TOOL = Tool(
    name="budget_calculator",
    description="Calculate optimal budget allocation for advertising campaigns across multiple platforms",
    inputSchema={
        "type": "object",
        "properties": {
            "budget": {"type": "number", "description": "Total advertising budget in USD"},
            "platforms": {"type": "array", "items": {"type": "string"}, "description": "List of platforms to advertise on"},
            "region": {"type": "string", "description": "Target region (e.g., 'southeast_asia')"},
            "duration_days": {"type": "integer", "description": "Campaign duration in days"}
        },
        "required": ["budget", "platforms", "region", "duration_days"]
    }
)

EFFECT_ANALYZER_TOOL = Tool(
    name="effect_analyzer",
    description="Analyze expected performance metrics for advertising campaigns",
    inputSchema={
        "type": "object",
        "properties": {
            "platform": {"type": "string", "description": "Platform to analyze"},
            "budget": {"type": "number", "description": "Budget allocated to this platform"},
            "target_audience": {"type": "string", "description": "Target audience description"},
            "campaign_type": {"type": "string", "description": "Type of campaign (awareness, conversion, etc.)"}
        },
        "required": ["platform", "budget", "target_audience", "campaign_type"]
    }
)

COMPLIANCE_CHECKER_TOOL = Tool(
    name="compliance_checker",
    description="Check advertising content compliance with regional regulations",
    inputSchema={
        "type": "object",
        "properties": {
            "platform": {"type": "string", "description": "Platform for compliance check"},
            "region": {"type": "string", "description": "Target region"},
            "ad_content": {"type": "string", "description": "Ad content to check"},
            "target_audience": {"type": "string", "description": "Target audience description"}
        },
        "required": ["platform", "region", "ad_content", "target_audience"]
    }
)

# Tool registry
AD_TOOLS = [
    BUDGET_CALCULATOR_TOOL,
    EFFECT_ANALYZER_TOOL,
    COMPLIANCE_CHECKER_TOOL,
    # Visual Autoregressive Modeling tool for ad image generation
    Tool(
        name="var_image_generator",
        description="Generate advertising images from text prompts (Visual Autoregressive Modeling)",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Text prompt describing the desired ad image"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "style": {"type": "string", "description": "Optional visual style"}
            },
            "required": ["prompt"]
        }
    )
]

# Tool execution mapping
TOOL_EXECUTORS = {
    "budget_calculator": budget_calculator_tool,
    "effect_analyzer": effect_analyzer_tool,
    "compliance_checker": compliance_checker_tool
}

# Register VAR executor
TOOL_EXECUTORS["var_image_generator"] = var_image_tool

# Tool registry
AD_TOOLS = [
    BUDGET_CALCULATOR_TOOL,
    EFFECT_ANALYZER_TOOL,
    COMPLIANCE_CHECKER_TOOL,
    Tool(
        name="var_image_generator",
        description="Generate advertising images from text prompts (Visual Autoregressive Modeling)",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Text prompt describing the desired ad image"},
                "width": {"type": "integer", "description": "Image width in pixels"},
                "height": {"type": "integer", "description": "Image height in pixels"},
                "style": {"type": "string", "description": "Optional visual style"}
            },
            "required": ["prompt"]
        }
    )
]

# Tool execution mapping (ensure VAR executor present)
TOOL_EXECUTORS = {
    "budget_calculator": budget_calculator_tool,
    "effect_analyzer": effect_analyzer_tool,
    "compliance_checker": compliance_checker_tool,
    "var_image_generator": var_image_tool
}