def silent_gap_index(
    infra_deficit_score: float, 
    complaint_density: float, 
    max_complaint_density: float, 
    vulnerability_score: float
) -> float:
    """
    Measures Voice Poverty: High physical deficit + low citizen reporting + high vulnerability.
    """
    if max_complaint_density <= 0:
        norm_complaints = 0.0
    else:
        norm_complaints = min(complaint_density / max_complaint_density, 1.0)
        
    sgi = infra_deficit_score * (1.0 - norm_complaints) * vulnerability_score
    return round(float(sgi), 3)


def spend_misalignment_index(
    infra_need_rank: int, 
    investment_rank: int, 
    total_districts: int
) -> float:
    """
    Measures Fiscal Disconnect: High need rank vs. low allocated public funding rank.
    Rank 1 = Highest Need / Highest Budget.
    """
    if total_districts <= 1:
        return 0.0
        
    smi = (investment_rank - infra_need_rank) / total_districts
    return round(float(smi), 3)
