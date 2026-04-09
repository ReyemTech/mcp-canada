"""MCP prompts for the Open Parliament module.

Provides guided workflow prompts and quick lookup templates for parliamentary data.
All prompts are bilingual (en/fr) via the lang parameter and use the parl_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def parl_research_bill(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a bill research workflow in the Canadian Parliament.

    Chains parl_search_bills -> parl_get_bill_details -> parl_get_votes
    to answer comprehensive questions about a federal bill.
    """
    if lang == "fr":
        return [
            Message(
                "Quel projet de loi souhaitez-vous rechercher? "
                "Vous pouvez fournir un numéro de projet de loi (ex: C-21, S-7) "
                "ou des mots-clés décrivant le sujet (ex: 'contrôle des armes à feu', 'immigration').",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser parl_search_bills pour trouver le projet de loi, "
                "puis parl_get_bill_details pour obtenir le texte complet et l'historique législatif, "
                "et enfin parl_get_votes pour voir comment la Chambre a voté sur ce projet de loi.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which bill would you like to research? "
            "You can provide a bill number (e.g., C-21, S-7) "
            "or keywords describing the topic (e.g., 'gun control', 'immigration').",
            role="user",
        ),
        Message(
            "I will first use parl_search_bills to find the bill, "
            "then parl_get_bill_details to retrieve the full text and legislative history, "
            "and finally parl_get_votes to see how the House voted on this bill.",
            role="assistant",
        ),
    ]


@prompt
async def parl_find_mp(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to look up a Member of Parliament by name or riding."""
    if lang == "fr":
        return (
            "Utilisez parl_get_politicians avec le nom du député pour chercher par nom, "
            "ou utilisez parl_search_by_riding avec un code postal ou le nom de la circonscription "
            "pour trouver le député de votre région."
        )
    return (
        "Use parl_get_politicians with the MP's name to search by name, "
        "or use parl_search_by_riding with a postal code or riding name "
        "to find your local Member of Parliament."
    )


@prompt
async def parl_track_voting(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through tracking how MPs voted in Parliament.

    Chains parl_get_votes -> parl_get_voting_record -> parl_get_ballots
    to provide a complete picture of voting patterns and individual MP ballots.
    """
    if lang == "fr":
        return [
            Message(
                "Quel sujet ou vote souhaitez-vous suivre? "
                "Je peux chercher des votes par mot-clé, session parlementaire ou numéro de vote. "
                "Je peux aussi afficher le bilan de vote d'un député spécifique.",
                role="user",
            ),
            Message(
                "Je vais utiliser parl_get_votes pour trouver les scrutins correspondants, "
                "puis parl_get_voting_record pour le bilan de vote d'un député, "
                "et parl_get_ballots pour les votes individuels sur un scrutin spécifique.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which topic or vote would you like to track? "
            "I can search votes by keyword, parliamentary session, or vote number. "
            "I can also show the voting record for a specific MP.",
            role="user",
        ),
        Message(
            "I will use parl_get_votes to find matching divisions, "
            "then parl_get_voting_record for an MP's voting history, "
            "and parl_get_ballots for individual ballot results on a specific vote.",
            role="assistant",
        ),
    ]


@prompt
async def parl_search_debates(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search Hansard debate transcripts by keyword."""
    if lang == "fr":
        return (
            "Utilisez parl_search_hansard avec un mot-clé pour chercher dans les débats parlementaires (Hansard). "
            "Vous pouvez filtrer par date ou par député. "
            "Utilisez parl_get_debates pour les transcriptions complètes d'une séance spécifique."
        )
    return (
        "Use parl_search_hansard with a keyword to search parliamentary debate transcripts (Hansard). "
        "You can filter by date or by MP name. "
        "Use parl_get_debates for full transcripts of a specific sitting."
    )


@prompt
async def parl_party_breakdown(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through comparing party representation in Parliament.

    Uses parl_get_party_members to retrieve membership for each party
    and compare seat counts and regional representation.
    """
    if lang == "fr":
        return [
            Message(
                "Quels partis souhaitez-vous comparer? "
                "Je peux afficher les membres du Parti conservateur (CPC), du Parti libéral (LPC), "
                "du NPD, du Bloc québécois (BQ) ou du Parti vert (GPC).",
                role="user",
            ),
            Message(
                "Je vais utiliser parl_get_party_members pour chaque parti afin de récupérer "
                "la liste des membres actuels, le nombre de sièges et la répartition régionale. "
                "Je présenterai un tableau comparatif de la représentation parlementaire.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which parties would you like to compare? "
            "I can show members of the Conservative Party (CPC), Liberal Party (LPC), "
            "NDP, Bloc Québécois (BQ), or Green Party (GPC).",
            role="user",
        ),
        Message(
            "I will use parl_get_party_members for each party to retrieve "
            "the current member list, seat count, and regional breakdown. "
            "I will present a comparative table of parliamentary representation.",
            role="assistant",
        ),
    ]
