import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai # type: ignore

# API-Key aus Umgebungsvariable
client = openai.OpenAI(api_key="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")

def frage_chatgpt_auswertung(ergebnisse):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein arbeitswissenschaftlicher Experte für flexible Arbeit in der zerspanenden Fertigung. Analysiere Mittelwerte neun betrieblicher Handlungsfelder, leite eine Clusterzuordnung gemäß dem MTOK-Modell ab und gib differenzierte, priorisierte Handlungsempfehlungen aus."
                },
                {
                    "role": "user",
                    "content": (
                        f"Die Mittelwerte der neun Handlungsfelder lauten:\n\n{ergebnisse}\n\n"
                        "Bitte führe folgende Schritte durch:\n"
                        "1. Gib eine kurze Bewertung des betrieblichen Reifegrads.\n"
                        "2. Ordne den Betrieb einem der folgenden Cluster zu:\n"
                        "   - Cluster 1: Traditionell und reaktiv\n"
                        "   - Cluster 2: Produktionsstark, aber mobilitätsfern\n"
                        "   - Cluster 3: Digital-affin und akzeptanzstark\n"
                        "   - Cluster 4: Effizient, aber strukturell gehemmt\n"
                        "3. Gib mindestens fünf priorisierte, praxisnahe Handlungsempfehlungen – gegliedert nach den vier MTOK-Dimensionen (Mensch, Technik, Organisation, Kultur)."
                    )
                }
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Fehler bei der GPT-Abfrage: {e}"



# Struktur der Anwendung
st.set_page_config(page_title="Readiness-Check", layout="wide")
st.title("Readiness-Check zur Einführung mobiler und zeitflexibler Arbeitsgestaltungen in der zerspanenden Fertigung")

# MTOK-Dimensionen und Handlungsfelder
mtok_structure = {
    "Mensch": ["Produktivität und Motivation", "Persönliches Umfeld"],
    "Technik": ["Arbeitsplatzgestaltung und Automatisierung", "IT-Systemlandschaft und digital vernetzte Infrastruktur"],
    "Organisation": ["Kommunikation, Kooperation und Zusammenarbeit", "Soziokulturelle und organisatorische Umwelt", "Produktionsorganisation"],
    "Kultur": ["Unternehmenskultur", "Soziale Beziehungen und Interaktion"]
}

Kriterien = {
    "Produktivität und Motivation": [
        {
            "frage": "M1.1 Beschäftigte wissen, welche Anforderungen mit zeitflexibler Arbeit verbunden sind.",
            "begründung": "Die zeitflexible Arbeit in der Zerspanung ist an technische Abläufe gebunden. Kenntnis über Konflikte (z. B. Maschinentaktung) ist Voraussetzung für realistische Umsetzung."
        },
        {
            "frage": "M1.2 Beschäftigte wissen, welche Anforderungen mobile Arbeit in der Fertigung stellt.",
            "begründung": "Mobile Arbeit erfordert Kenntnisse zu IT-Zugriff, Prozessintegration und Selbstorganisation. Unklare Regelungen führen zu Produktivitätsverlust."
        },
        {
            "frage": "M1.3 Beschäftigte verfügen über die fachlichen und digitalen Kompetenzen zur Selbststeuerung.",
            "begründung": "Eigenverantwortliche Prozesskontrolle und Informationsverarbeitung sind zentrale Voraussetzungen für produktive Flexibilität."
        },
        {
            "frage": "M1.4 Beschäftigte verfügen über einen vielseitigen Aufgabenkatalog (z. B. Programmierung, Planung, Dokumentation).",
            "begründung": "Vielfältige Aufgabeninhalte fördern ein vertieftes Systemverständnis, stärken die Eigenverantwortung und erhöhen die Anschlussfähigkeit an mobile oder flexible Arbeit."
        },
        {
            "frage": "M1.5 Beschäftigte sind in der Lage, bei Störungen eigenständig Lösungen zu finden.",
            "begründung": "In flexiblen Modellen kann nicht immer sofort Hilfe erfolgen. Handlungskompetenz bei Prozessabweichungen sichert Produktivität."
        },
        {
            "frage": "M1.6 Es finden regelmäßige Feedbackgespräche zur Leistung unter flexiblen Bedingungen statt.",
            "begründung": "Feedback fördert Motivation, korrigiert Fehlentwicklungen und unterstützt individuelle Weiterentwicklung."
        },
        {
            "frage": "M1.7 Die Arbeitsumgebung ermöglicht produktives Arbeiten bei räumlicher Entkopplung.",
            "begründung": "Ergonomische, akustische und digitale Bedingungen sind Voraussetzung für Konzentration und Leistung auch außerhalb der Fertigungshalle."
        },
        {
            "frage": "M1.8 Beschäftigte zeigen Bereitschaft zur Mitgestaltung flexibler Arbeitsformen.",
            "begründung": "Beteiligung fördert Akzeptanz, Nutzung und Wirksamkeit flexibler Arbeitsmodelle."
        },
        {
            "frage": "M1.9 Der Betrieb schafft Räume zur Erprobung neuer Arbeitsweisen.",
            "begründung": "Erprobung in sicherem Rahmen reduziert Ängste, fördert Lernprozesse und Innovation."
        },
        {
            "frage": "M1.10 Engagement in der Arbeitsgestaltung wird sichtbar anerkannt.",
            "begründung": "Anerkennung verstärkt gewünschtes Verhalten und motiviert zur Beteiligung."
        },
        {
            "frage": "M1.11 Leistungsziele sind klar definiert und transparent.",
            "begründung": "Klare Ziele fördern Eigenverantwortung, Orientierung und produktives Arbeiten – unabhängig vom Ort."
        },
        {
            "frage": "M1.12 Leistungsschwächere Mitarbeitende werden gezielt unterstützt.",
            "begründung": "Flexible Modelle dürfen nicht zu Ausschluss führen – individuelle Förderung stärkt Integration und Leistung."
        },
        {
            "frage": "M1.13 Erfahrungswissen wird dokumentiert und regelmäßig weitergegeben.",
            "begründung": "Wissenstransfer verhindert Qualitätsverluste in Teams mit wechselnden Präsenzzeiten."
        },
        {
            "frage": "M1.14 Engagierte Beschäftigte erhalten gezielte Entwicklungsangebot.",
            "begründung": "Entwicklungsperspektiven erhalten Motivation und fördern langfristige Bindung."
        },
        {
            "frage": "M1.15 Teamleistungen werden ebenso wertgeschätzt wie individuelle Beiträge.",
            "begründung": "Flexible Arbeit erfordert Teamzusammenarbeit – ihre Anerkennung stärkt sozialen Zusammenhalt."
        },
        {
            "frage": "M1.16 Es existieren Verfahren zur Früherkennung von Demotivation.",
            "begründung": "Früherkennung (z. B. durch regelmäßige Gespräche) sichert Leistung und ermöglicht rechtzeitige Intervention."
        },
        {
            "frage": "M1.17 Beschäftigte reflektieren die Wirkung flexibler Arbeit auf ihre Produktivität.",
            "begründung": "Reflexion fördert Selbststeuerung und kontinuierliche Verbesserung – zentrale Elemente lernender Organisationen."
        }
    ],
    "Persönliches Umfeld": [
        {
            "frage": "M2.1 Beschäftigte sind offen gegenüber zeitflexibler Arbeit.",
            "begründung": "Eine positive Grundhaltung fördert Akzeptanz und Beteiligung an Flexibilisierungsprozessen."
        },
        {
            "frage": "M2.2 Beschäftigte sind offen gegenüber mobiler Arbeit.",
            "begründung": "Eine positive Grundhaltung fördert Akzeptanz und Beteiligung an Flexibilisierungsprozessen."
        },
        {
            "frage": "M2.3 Beschäftigte erkennen persönliche Vorteile in mobiler oder zeitflexibler Arbeit.",
            "begründung": "Subjektiv empfundener Nutzen wirkt motivationsfördernd und stabilisiert neue Arbeitsweisen."
        },
        {
            "frage": "M2.4 Beschäftigte fühlen sich gut vorbereitet auf mobile oder zeitflexible Arbeit.",
            "begründung": "Sicherheit in der Ausführung stärkt Selbstwirksamkeit und Engagement."
        },
        {
            "frage": "M2.5 Beschäftigte identifizieren sich mit ihrer täglichen Arbeit.",
            "begründung": "Identifikation steigert Eigenverantwortung und Leistungsbereitschaft."
        },
        {
            "frage": "M2.6 Beschäftigte identifizieren sich mit dem Unternehmen.",
            "begründung": "Verbundenheit mit der Organisation unterstützt Loyalität und Veränderungsbereitschaft."
        },
        {
            "frage": "M2.7 Die Beschäftigten beherrschen gängige digitale Tools (z. B. E-Mail, Team-Chat, Maschineninterfaces).",
            "begründung": "Praktische Anwendungskompetenz ist Voraussetzung für effektive digitale Kollaboration."
        },
        {
            "frage": "M2.8 Beschäftigte können kleinere Probleme mit digitalen Tools selbstständig lösen oder umgehen.",
            "begründung": "Digitale Selbstwirksamkeit stärkt Autonomie und Handlungsfähigkeit in mobilen Arbeitsformen."
        },
        {
            "frage": "M2.9 Beschäftigte zeigen Interesse an Weiterqualifizierung im Bereich digitaler Kompetenzen.",
            "begründung": "Lernbereitschaft ist Grundlage für die Anpassungsfähigkeit an technologische Entwicklungen."
        },
        {
            "frage": "M2.10 Beschäftigte verfügen über stabile externe Bedingungen für mobile Arbeit (z. B. Rückzugsort, soziales Umfeld).",
            "begründung": "Die Umsetzbarkeit flexibler Arbeit hängt auch von der häuslichen Situation ab."
        },
        {
            "frage": "M2.11 Beschäftigte empfinden digitale Systeme im Alltag als hilfreich.",
            "begründung": "Positive Nutzungserfahrungen fördern Offenheit und Integration neuer Technologien."
        },
        {
            "frage": "M2.12 Beschäftigte reflektieren regelmäßig ihre Erfahrungen mit mobilen oder flexiblen Arbeitsformen.",
            "begründung": "Reflexion unterstützt Lernprozesse und ermöglicht kontinuierliche Anpassung."
        },
        {
            "frage": "M2.13 Beschäftigte bringen Verbesserungsvorschläge zu digitalen Arbeitsmitteln aktiv ein.",
            "begründung": "Beteiligung an der Systemgestaltung fördert Akzeptanz und Passung."
        },
        {
            "frage": "M2.14 Beschäftigte kommunizieren Bedarfe und Herausforderungen im Umgang mit digitalen Tools offen.",
            "begründung": "Transparenz ermöglicht bedarfsgerechte Unterstützung."
        },
        {
            "frage": "M2.15 Beschäftigte verstehen grundlegende Funktionsweisen vernetzter digitaler Systeme.",
            "begründung": "Systemverständnis erhöht Sicherheit und reduziert Fehleranfälligkeit."
        },
        {
            "frage": "M2.16 Beschäftigte können ihre digitale Arbeit gegenüber anderen erklären oder anleiten.",
            "begründung": "Vermittlungsfähigkeit ist Zeichen für tiefere Durchdringung und Teamfähigkeit."
        },
        {
            "frage": "M2.17 Beschäftigte sind in relevante Abstimmungsprozesse zu digitalen und flexiblen Arbeitsformen eingebunden.",
            "begründung": "Beteiligung stärkt Identifikation und verbessert Akzeptanz."
        }
    ],
    "Arbeitsplatzgestaltung und Automatisierung": [
        {
            "frage": "T1.1 Die Werkzeugmaschine kann ohne ständige Beaufsichtigung betrieben werden (z. B. mannlose Schicht).",
            "begründung": "Ein hoher Automatisierungsgrad erlaubt zeitliche Entkopplung und ermöglicht mobile oder zeitflexible Schichtanteile."
        },
        {
            "frage": "T1.2 Automatisierung ersetzt präsenzpflichtige Routinetätigkeiten (z. B. Werkstückhandling).",
            "begründung": "Automatisierung steigert Produktivität und erweitert Spielräume für mobile Einheiten."
        },
        {
            "frage": "T1.3 Präsenzpflichtige Aufgaben (z. B. Maschineneinrichtung) können aggregiert werden.",
            "begründung": "Zusammenfassung ermöglicht planbare Präsenzzeiten, erleichtert Schichtorganisation und reduziert Unterbrechungen."
        },
        {
            "frage": "T1.4 Maschinenbedienung erfolgt über standardisierte und dokumentierte Arbeitsabläufe.",
            "begründung": "Standardisierung ist Grundlage für übertragbare Aufgaben, Schulung und Fernsteuerbarkeit."
        },
        {
            "frage": "T1.5 Maschinenprozesse sind stabil und störungsarm.",
            "begründung": "Prozessstabilität ist Voraussetzung für entkoppelte Arbeit und reduziert ungeplante Eingriffe."
        },
        {
            "frage": "T1.6 Fernüberwachung und Eingriff von Maschinenprozessen ist technisch realisiert (z. B. Kameras, Monitoring-Apps).",
            "begründung": "Visuelle und sensorische Fernkontrolle reduziert Präsenznotwendigkeit bei Routineüberwachung."
        },
        {
            "frage": "T1.7 Automatisierte Fehlermeldesysteme (z. B. akustisch, visuell, digital) sind vorhanden.",
            "begründung": "Unterstützt frühzeitige Intervention ohne ständige Präsenz; verringert Reaktionszeit."
        },
        {
            "frage": "T1.8 CNC-Maschinen sind netzwerkfähig und ermöglichen Datenaustausch in Echtzeit.",
            "begründung": "Vernetzte Maschinen bilden die Grundlage digitaler Prozessintegration und Steuerung."
        },
        {
            "frage": "T1.9 Arbeitsplatzsysteme (z. B. HMI, Tablets) sind mobil nutzbar über verlässliche Schnittstellen zu digitalen Systemen (z. B. ERP, MES).",
            "begründung": "Mobile Interfaces unterstützen dezentrale Steuerung, z. B. bei Maschinenstörung oder Nachjustierung."
        },
        {
            "frage": "T1.10 Prüf- und Qualitätssicherungsprozesse erfolgen automatisiert oder sind entkoppelt.",
            "begründung": "Reduziert zeitliche Fixpunkte, schafft Flexibilität im Ablauf."
        },
        {
            "frage": "T1.11 Wartungsbedarfe und Eingriffsprotokolle sind digital dokumentiert und zugänglich.",
            "begründung": "Transparente Dokumentation ermöglicht Übergaben, Eigenverantwortung und hybride Betreuung."
        },
        {
            "frage": "T1.12 Der Maschinenpark erlaubt Mehrmaschinenbedienung durch einzelne Beschäftigt.",
            "begründung": "Höhere Selbststeuerung und zeitliche Puffer entstehen durch koordinierte Maschinenführung."
        },
        {
            "frage": "T1.13 Echtzeitdaten zur Maschinenauslastung stehen zur Verfügung (z. B. OEE-Analyse).",
            "begründung": "Grundlage für dynamische Prozesssteuerung auch bei flexibler Anwesenheit."
        },
        {
            "frage": "T1.14 Fertigungsinseln oder Gruppenarbeitssysteme fördern flexible Verantwortungsaufteilung.",
            "begründung": "Unterstützt Teamsteuerung und gegenseitige Vertretung bei mobiler Arbeit."
        },
        {
            "frage": "T1.15 Maschinenarbeitsplätze verfügen über verlässliche Schnittstellen zu digitalen Systemen (z. B. ERP, MES).",
            "begründung": "Digitale Integration ist Grundvoraussetzung für ortsunabhängige Planung, Steuerung und Dokumentation."
        },
        {
            "frage": "T1.16 Der Automatisierungsgrad wird regelmäßig bewertet und gezielt weiterentwickel.",
            "begründung": "Kontinuierliche Verbesserung sichert langfristig Flexibilisierungsfähigkeit."
        },
        {
            "frage": "T1.17 Auswirkungen flexibler Arbeit auf Produktivität und Maschinenauslastung werden systematisch erhoben.",
            "begründung": "Monitoring und Datenbasis ermöglichen Anpassung und Optimierung flexibler Modelle im Produktionskontext."
        }
    ],
    "IT-Systemlandschaft und digital vernetzte Infrastruktur": [
        {
            "frage": "T2.1 Die IT-Infrastruktur stellt mobile Endgeräte zur Verfügung.",
            "begründung": "Grundlage für mobile Arbeit ist die Verfügbarkeit und Ausstattung mit mobilen Endgeräten wie Laptops oder Tablets."
        },
        {
            "frage": "T2.2 Die IT-Infrastruktur ermöglicht ortsunabhängigen Zugriff auf relevante Systeme (z. B. ERP, MES).",
            "begründung": "Mobiles Arbeiten erfordert gesicherten Zugriff auf zentrale Anwendungen, z. B. über VPN oder cloudbasierte Lösungen."
        },
        {
            "frage": "T2.3 Beschäftigte haben Zugriff auf digitale Kommunikations- und Kollaborationstools (z. B. MS Teams).",
            "begründung": "Digitale Kommunikation ersetzt Präsenzkontakte und ermöglicht dezentrale Abstimmungen in Echtzeit."
        },
        {
            "frage": "T2.4 Es bestehen unternehmensweit einheitliche Standards für mobile Endgeräte und Software.",
            "begründung": "Standardisierung erhöht Sicherheit, Wartbarkeit und Nutzungskomfort mobiler Arbeitsmittel."
        },
        {
            "frage": "T2.5 Der IT-Support ist ortsunabhängig verfügbar.",
            "begründung": "Verfügbarkeit bei Problemen sichert Stabilität und erhöht Akzeptanz und Produktivität mobiler Arbeit."
        },
        {
            "frage": "T2.6 Die eingesetzten IT-Systeme sind zukunftsfähig und modular erweiterbar.",
            "begründung": "Anschlussfähigkeit sichert langfristige Flexibilität und Integration neuer Tools."
        },
        {
            "frage": "T2.7 Es existieren sichere Zugriffskonzepte mit klaren Rollen und Rechten.",
            "begründung": "Klare Zugriffsrechte schützen Daten, erhöhen Vertrauen und erlauben eine skalierbare Nutzung."
        },
        {
            "frage": "T2.8 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
            "begründung": "Echtzeitintegration zwischen Bereichen ermöglicht schnelle Entscheidungen und flexible Steuerung."
        },
        {
            "frage": "T2.9 IT-Sicherheit ist systematisch für hybride Arbeitsformen geregelt.",
            "begründung": "Sicherheitskonzepte müssen mobil adaptierbar sein, um Datenrisiken zu vermeiden."
        },
        {
            "frage": "T2.10 Digitale Schulungsangebote sind in die IT-Systemlandschaft integriert.",
            "begründung": "Kompetenzförderung stärkt Systemnutzung, sichert Handlungsfähigkeit und reduziert Unsicherheit."
        },
        {
            "frage": "T2.11 Die Digitalisierung ist strategisch im Unternehmen verankert.",
            "begründung": "Eine strategische Zielsetzung erhöht die Ressourcenbindung und fördert die konsequente Umsetzung."
        },
        {
            "frage": "T2.12 Produktions- und IT-Bereiche stimmen sich regelmäßig zur Digitalisierung ab.",
            "begründung": "Interdisziplinäre Abstimmung fördert ganzheitliche Umsetzung und reduziert Schnittstellenprobleme."
        },
        {
            "frage": "T2.13 Der Einsatz digitaler Systeme wird regelmäßig evaluiert und verbessert.",
            "begründung": "Systematische Optimierung erhöht Akzeptanz, Effizienz und Benutzerfreundlichkeit."
        },
        {
            "frage": "T2.14 Mobile Arbeitsplätze verfügen über abgesicherte Datenverbindungen und Authentifizierungsmechanismen.",
            "begründung": "Datenschutz und -sicherheit sind Voraussetzung für dezentrale Prozessbeteiligung."
        },
        {
            "frage": "T2.15 Betriebsvereinbarungen regeln Einsatz, Nutzung und Kontrolle digitaler Systeme.",
            "begründung": "Rechtliche und organisationale Klarheit stärkt Vertrauen und verhindert Missverständnisse."
        },
        {
            "frage": "T2.16 IT-Weiterbildung ist fester Bestandteil der betrieblichen Qualifizierungsstrategie.",
            "begründung": "Digitale Befähigung ist Grundlage für Transformation und Flexibilität im Produktionsumfeld."
        },
        {
            "frage": "T2.17 Simulationen oder digitale Zwillinge unterstützen Planung und Steuerung der Produktion.",
            "begründung": "Vorausschauende Modellierung reduziert Planungsunsicherheiten und erhöht Reaktionsfähigkeit."
        },
        {
            "frage": "T2.18 Beschäftigte können Schulungsinhalte zu IT-Systemen zeit- und ortsunabhängig abrufen.",
            "begründung": "Flexibles Lernen stärkt Eigenverantwortung und Integration ins Tagesgeschäft."
        },
        {
            "frage": "T2.19 Es existieren zentrale Dashboards zur Produktions- und Anlagensteuerung.",
            "begründung": "Zentralisierte Übersicht erhöht Transparenz, erlaubt Priorisierung und Reaktion ohne physischen Zugriff."
        },
        {
            "frage": "T2.20 Produktionsrelevante Daten (z. B. Störungen) sind in Echtzeit für Berechtigte verfügbar.",
            "begründung": "Informationsfluss und Koordination werden verbessert – Voraussetzung für dezentrale Steuerung."
        }
    ],
        "Kommunikation, Kooperation und Zusammenarbeit": [
        {
            "frage": "O1.1 Es bestehen strukturierte Kanäle für den Wissenstransfer zwischen Arbeitsbereichen.",
            "begründung": "Stabilisierter Wissenstransfer erhöht Resilienz und Ausfallkompensation bei mobil-flexiblen Arbeitsformen."
        },
        {
            "frage": "O1.2 Relevante Informationen werden zeitnah, digital und adressatengerecht kommuniziert.",
            "begründung": "Effektive Kommunikation ist Basis für dezentrale Koordination."
        },
        {
            "frage": "O1.3 Kommunikationskanäle sind auch bei Schichtübergaben oder Vertretungsszenarien verlässlich nutzbar.",
            "begründung": "In der zerspanenden Fertigung treten häufig Wechsel und Übergaben auf."
        },
        {
            "frage": "O1.4 Die eingesetzten Kommunikationsmittel sind standardisiert und klar zugewiesen.",
            "begründung": "Einheitliche Tools reduzieren Medienbrüche und erhöhen Effizienz."
        },
        {
            "frage": "O1.5 Verbindliche Regeln zur IT-Nutzung (z. B. VPN, Remote-Zugriffe) sind etabliert und bekannt.",
            "begründung": "Sicherheit und Klarheit fördern Compliance und Verlässlichkeit."
        },
        {
            "frage": "O1.6 Die Organisation fördert abteilungsübergreifende Zusammenarbeit aktiv.",
            "begründung": "Mobile und zeitflexible Arbeit erfordert intensivere Zusammenarbeit über Bereichsgrenzen hinweg."
        },
        {
            "frage": "O1.7 Hybride Meetings (Präsenz und Remote) sind etabliert und technisch unterstützt.",
            "begründung": "Hybride Formate ermöglichen inklusive Zusammenarbeit bei Ortsflexibilität."
        },
        {
            "frage": "O1.8 Entscheidungsprozesse sind dokumentiert und für Beteiligte zugänglich.",
            "begründung": "Transparenz ersetzt physische Nähe als Steuerungsinstrument."
        },
        {
            "frage": "O1.9 Kommunikationsziele und -prozesse werden regelmäßig reflektiert und angepasst.",
            "begründung": "Kommunikation muss sich an wandelnde Anforderungen anpassen."
        },
        {
            "frage": "O1.10 Neue Beschäftigte werden strukturiert in Kommunikations- und Kollaborationsprozesse eingeführt.",
            "begründung": "Strukturierte Einarbeitung sichert Integration in mobile Arbeitsweisen."
        },
        {
            "frage": "O1.11 Projektinformationen sind für Beteiligte digital, aktuell und zentral zugänglich.",
            "begründung": "Transparenz verhindert Wissensinseln und erleichtert Zusammenarbeit."
        },
        {
            "frage": "O1.12 Beschäftigte wissen, welche Kanäle im Störungsfall zu nutzen sind.",
            "begründung": "Klare Kommunikationswege sichern Handlungsfähigkeit bei Abweichungen."
        },
        {
            "frage": "O1.13 Digitale Kommunikationskompetenz wird systematisch gefördert.",
            "begründung": "Mediensouveränität ist Voraussetzung für gelingende digitale Zusammenarbeit."
        },
        {
            "frage": "O1.14 Feedbackprozesse zwischen Führung und Beschäftigten sind etabliert.",
            "begründung": "Rückmeldung stärkt die Qualität der Zusammenarbeit und fördert Kulturwandel."
        },
        {
            "frage": "O1.15 Beteiligungsformate (z. B. digitale Abstimmungen) sind etabliert und niederschwellig zugänglich.",
            "begründung": "Beteiligung stärkt Identifikation, verringert Widerstand und erhöht Umsetzungschancen."
        },
        {
            "frage": "O1.16 Die eingesetzten digitalen Tools unterstützen die Zusammenarbeit (z. B. gemeinsame Plattformen).",
            "begründung": "Gemeinsames Arbeiten erfordert Zugriff auf zentrale Informationsressourcen."
        },
        {
            "frage": "O1.17 Bei Ziel- oder Koordinationsproblemen werden Kommunikationsstrukturen gezielt angepasst.",
            "begründung": "Lernende Kommunikation verbessert langfristig die Wirksamkeit der Kooperation."
        },
        {
            "frage": "O1.18 Die Organisation reflektiert regelmäßig die Wirkung von Zeitautonomie auf Zusammenarbeit und Kommunikation.",
            "begründung": "Flexible Arbeit verändert Abstimmungsprozesse und ihre Passung muss laufend geprüft werden."
        }
    ],
    "Soziokulturelle und organisatorische Umwelt": [
        {
            "frage": "O2.1 Der Betrieb verfügt über ausreichend qualifizierte Fachkräfte in der zerspanenden Fertigung.",
            "begründung": "Fachkräftesicherung ist Grundvoraussetzung für produktive Flexibilität. Ohne geeignete Kompetenzen scheitern mobile oder zeitflexible Modelle bereits in der Planung."
        },
        {
            "frage": "O2.2 Die Personalplanung berücksichtigt gezielt den flexiblen Einsatz über Arbeitszeiten und Orte hinweg.",
            "begründung": "Proaktive Planung schafft Ressourcen für Flexibilität, insbesondere in Schichtbetrieben oder bei variantenreicher Fertigung."
        },
        {
            "frage": "O2.3 Betriebsvereinbarungen regeln klar die Anwendung mobiler und zeitflexibler Arbeit.",
            "begründung": "Verbindliche Regelwerke geben Orientierung und Rechtssicherheit – in Cluster 3 als Erfolgsfaktor beschrieben."
        },
        {
            "frage": "O2.4 Externe Anforderungen (z. B. Kunden, Lieferanten) werden in der Flexibilitätsstrategie berücksichtigt.",
            "begründung": "Nur wenn Schnittstellen abgestimmt sind, lassen sich flexible Modelle durchgängig realisieren."
        },
        {
            "frage": "O2.5 Rechtliche Rahmenbedingungen (z. B. ArbZG, DSGVO) sind bekannt und werden umgesetzt.",
            "begründung": "Rechtssicherheit ist Voraussetzung für nachhaltige Modelle. Unsicherheit führt zu Zurückhaltung."
        },
        {
            "frage": "O2.6 Die Organisation informiert über arbeitsrechtliche, sicherheitsrelevante und gesundheitliche Risiken.",
            "begründung": "Aufklärung über Homeoffice-Ergonomie, Datenschutz, psychische Belastungen stärkt sichere Anwendung."
        },
        {
            "frage": "O2.7 Schulungsangebote zu rechtlichen und organisatorischen Aspekten flexibler Arbeit sind etabliert.",
            "begründung": "Befähigung der Beschäftigten zur regelkonformen Nutzung erhöht Beteiligung und reduziert Widerstände."
        },
        {
            "frage": "O2.8 Arbeitszeitmodelle sind in Planungs- und Steuerungssysteme integriert (z. B. MES, ERP).",
            "begründung": "Nur wenn Systeme eingebunden sind, sind flexible Modelle praxistauglich und steuerbar."
        },
        {
            "frage": "O2.9 Die Aufbau- und Ablauforganisation ist anpassungsfähig (z. B. bei Sonderaufträgen oder Vertretungen).",
            "begründung": "Starre Strukturen behindern spontane Reaktion – Cluster 2/4 zeigten hier hohe Hürden."
        },
        {
            "frage": "O2.10 Verantwortung von Führung für Flexibilisierung ist definiert und implementiert.",
            "begründung": "Unklare Rollenerwartung führt zu Stillstand. Führung ist zentrale Instanz für Umsetzung und Steuerung."
        },
        {
            "frage": "O2.11 Die Kommunikation zu Regelungen und Erwartungen flexibler Arbeit ist klar strukturiert.",
            "begründung": "Klarheit stärkt Vertrauen, verhindert Missverständnisse und Überlastung."
        },
        {
            "frage": "O2.12 Ansprechpersonen für Fragen zur flexiblen Arbeit sind bekannt.",
            "begründung": "Niedrigschwellige Unterstützung erhöht Anwendungsrate und reduziert Fehler."
        },
        {
            "frage": "O2.13 Vereinbarkeit von Arbeit und Privatleben ist explizites Ziel der Flexibilitätsstrategie.",
            "begründung": "Flexibilität erhöht nur dann Produktivität, wenn sie auch Bedürfnisse der Beschäftigten berücksichtigt."
        },
        {
            "frage": "O2.14 Zuständigkeiten und Vertretungen sind auch bei mobiler Arbeit eindeutig geregelt.",
            "begründung": "Klare Verantwortlichkeiten sichern Prozessstabilität und entlasten das Team."
        },
        {
            "frage": "O2.15 Die Organisation analysiert regelmäßig Personalverfügbarkeit und Belastungsspitzen.",
            "begründung": "Nur mit Kapazitätstransparenz lassen sich Mobilität und Flexibilität realisieren."
        },
        {
            "frage": "O2.16 Feedback zur Umsetzung mobiler und zeitflexibler Arbeit wird systematisch eingeholt und genutzt.",
            "begründung": "Beteiligung der Beschäftigten stärkt Realitätsbezug und Anpassungsfähigkeit."
        },
        {
            "frage": "O2.17 Die Beschäftigten können Beginn und Ende ihrer täglichen Arbeitszeit mitgestalten.",
            "begründung": "Ein signifikanter Einfluss auf flexible Arbeitsmodelle wurde empirisch belegt."
        },
        {
            "frage": "O2.18 Pausenzeiten können im Rahmen betrieblicher Vorgaben flexibel gestaltet werden.",
            "begründung": "Autonomie über Pausen wirkt positiv auf Erholung, Effizienz und Zeitautonomie."
        }
    ],
    "Produktionsorgansiation": [
        {
            "frage": "O3.1 Die Aufgaben sind hinsichtlich ihrer Präsenzpflicht analysiert und systematisch aufteilbar.",
            "begründung": "Differenzierung präsenzkritischer und mobil bearbeitbarer Aufgaben ist Voraussetzung für Flexibilität."
        },
        {
            "frage": "O3.2 Die durchschnittliche Losgröße ermöglicht kurzfristige Umplanungen.",
            "begründung": "Kleine Lose sind mit höherer Dispositionsfreiheit verbunden – laut Regressionsanalyse negativ korreliert mit Flexibilitätshindernissen."
        },
        {
            "frage": "O3.3 Lauf- und Durchlaufzeiten sind optimiert und stabil steuerbar.",
            "begründung": "Lange Laufzeiten wurden in der Regressionsanalyse als Flexibilitätshindernis identifiziert."
        },
        {
            "frage": "O3.4 Die Produktionsplanung ist mit flexiblen Zeitmodellen kompatibel.",
            "begründung": "Zeitflexibilität erfordert Planungsinstrumente, die variable Anwesenheitszeiten abbilden können."
        },
        {
            "frage": "O3.5 Die Schicht- und Einsatzplanung ist dynamisch anpassbar.",
            "begründung": "Starre Planungssysteme reduzieren Handlungsspielräume und wirken flexibilitätshemmend."
        },
        {
            "frage": "O3.6 Ausweichkapazitäten bei Personalengpässen sind eingeplant.",
            "begründung": "Personelle Puffer ermöglichen kurzfristige Anpassung an variable Arbeitszeitwünsche."
        },
        {
            "frage": "O3.7 Rüstzeiten sind kurz, standardisiert und in die Planung integriert.",
            "begründung": "Kurze und standardisierte Rüstprozesse erleichtern flexible Schichtmodelle und kurzfristige Umplanungen."
        },
        {
            "frage": "O3.8 Instandhaltungsprozesse sind planbar und beeinträchtigen den Produktionsfluss nicht unnötig.",
            "begründung": "Planbare Instandhaltung schafft Freiräume für zeitflexible Gestaltung, insbesondere in Nebenzeiten."
        },
        {
            "frage": "O3.9 Die Produktionssteuerung erlaubt dezentrale Anpassungen durch operative Führungsebenen.",
            "begründung": "Dezentrale Steuerung erhöht Reaktionsgeschwindigkeit bei flexiblen Arbeitszeiten."
        },
        {
            "frage": "O3.10 Bei Maschinenstillstand entstehen keine unmittelbaren kritischen Produktivitätsverluste.",
            "begründung": "Die Toleranz gegenüber kurzfristiger Nichtbesetzung erlaubt mehr Zeitautonomie."
        },
        {
            "frage": "O3.11 Qualitätskontrollen sind prozessintegriert oder digital unterstützt.",
            "begründung": "Digitale Prüfprozesse ermöglichen Entkopplung von Ort und Zeit."
        },
        {
            "frage": "O3.12 Die Auftragssteuerung ist dynamisch und mit digitalen Schnittstellen vernetzt.",
            "begründung": "Echtzeitsteuerung und digitale Integration sind Grundlage für Flexibilisierung."
        },
        {
            "frage": "O3.13 Produktionsprozesse sind standardisiert dokumentiert und für andere übertragbar.",
            "begründung": "Standardisierung erhöht die Planbarkeit und Vertretbarkeit bei wechselnden Zuständigkeiten."
        },
        {
            "frage": "O3.14 Arbeitsorganisation erlaubt kurzfristige Aufgabenverlagerungen im Team.",
            "begründung": "Flexibilität erfordert operative Vertretungs- und Umverteilungsmechanismen."
        },
        {
            "frage": "O3.15 Beschäftigte können Prioritäten in ihrem Aufgabenbereich selbst setzen.",
            "begründung": "Eigenverantwortliche Steuerung ist Grundvoraussetzung für produktive Flexibilität."
        },
        {
            "frage": "O3.16 Aufgabenverfolgung und Zielstatus sind digital transparent.",
            "begründung": "Transparente Abläufe unterstützen mobile Kontrolle, Feedback und Steuerung."
        },
        {
            "frage": "O3.17 Sonder- und Einzelteilfertigung ist klar von Serienproduktion organisatorisch getrennt.",
            "begründung": "Getrennte Prozesse erleichtern flexible Planung in stabilen Serienumgebungen."
        }
    ],
    "Unternehmenskultur": [
        {
            "frage": "K1.1 Im Unternehmen wird Vertrauen als Grundlage der Zusammenarbeit gelebt.",
            "begründung": "Vertrauen ist elementar für mobile Arbeit, da Kontrolle nicht durch physische Präsenz möglich ist."
        },
        {
            "frage": "K1.2 Beschäftigte erhalten Handlungsfreiräume zur Gestaltung ihrer Arbeit.",
            "begründung": "Handlungsspielraum stärkt Motivation, Eigenverantwortung und Innovationspotenzial."
        },
        {
            "frage": "K1.3 Zielerreichung steht über Anwesenheit.",
            "begründung": "Leistungskultur fokussiert auf Ergebnisse statt auf Präsenz, besonders relevant in hybriden Settings."
        },
        {
            "frage": "K1.4 Flexible Arbeit wird nicht mit Produktivitätsverlust assoziiert.",
            "begründung": "Vorurteile über Mobilität behindern Akzeptanz und Einführung."
        },
        {
            "frage": "K1.5 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
            "begründung": "Transformationsbereitschaft ist Voraussetzung für Flexibilisierung."
        },
        {
            "frage": "K1.6 Die Fehlerkultur ist konstruktiv und unterstützend.",
            "begründung": "Fehlerfreundlichkeit fördert Innovation und Lernen, besonders bei neuen Arbeitsweisen."
        },
        {
            "frage": "K1.7 Die Unternehmensführung leben Flexibilität sichtbar vor.",
            "begründung": "Vorbildfunktion der Führung prägt kulturelle Normen und Öffnung."
        },
        {
            "frage": "K1.8 Leistung wird anhand von Ergebnissen und Zielbeiträgen bewertet.",
            "begründung": "Leistungsmanagement muss mit mobilen Konzepten vereinbar sein."
        },
        {
            "frage": "K1.9 Im Unternehmen ist eine Kultur des Lernens verankert.",
            "begründung": "Lernbereitschaft ist Voraussetzung für den Umgang mit technischer und organisatorischer Dynamik."
        },
        {
            "frage": "K1.10 Flexible Arbeit wird als Bestandteil der betrieblichen Normalität wahrgenommen.",
            "begründung": "Normalisierung senkt Widerstände und verankert Flexibilität langfristig."
        },
        {
            "frage": "K1.11 Es bestehen keine verdeckten Erwartungen an ständige Erreichbarkeit.",
            "begründung": "Entgrenzung wirkt kontraproduktiv für Work-Life-Balance und nachhaltige Nutzung."
        },
        {
            "frage": "K1.12 Unterschiedliche Arbeitsstile und Rhythmen werden akzeptiert.",
            "begründung": "Heterogenität fördert Anpassungsfähigkeit und Individualisierung."
        },
        {
            "frage": "K1.13 Mobile Arbeit wird in Teamabstimmungen berücksichtigt.",
            "begründung": "Kulturelle Integration benötigt Abstimmung und explizite Einbindung.."
        },
        {
            "frage": "K1.14 Die Akzeptanz flexibler Arbeit wird systematisch erfasst.",
            "begründung": "Feedback hilft kulturelle Barrieren zu identifizieren und abzubauen."
        },
        {
            "frage": "K1.15 Kulturelle Unterschiede innerhalb von Teams werden berücksichtigt.",
            "begründung": "Interkulturelle Sensibilität ist bei hybriden Teams zunehmend relevant."
        },
        {
            "frage": "K1.16 Das Unternehmen reflektiert regelmäßig seine Kultur im Umgang mit Neuerungen.",
            "begründung": "Reflexionsprozesse unterstützen kontinuierliche Entwicklung."
        },
        {
            "frage": "K1.17 Die Einbindung der Beschäftigten in Veränderungsprozesse ist institutionalisiert.",
            "begründung": "Beteiligung stärkt Legitimation und kulturelle Anschlussfähigkeit."
        },
        {
            "frage": "K1.18 Fehler im Umgang mit neuen Arbeitsformen werden als Lernchance begriffen.",
            "begründung": "Eine konstruktive Fehlerkultur ist Voraussetzung für sichere Lernprozesse."
        },
        {
            "frage": "K1.19 Die Organisation spricht offen über Zielkonflikte zwischen Flexibilität und Produktionssicherheit.",
            "begründung": "Realistische Diskussionen fördern Vertrauen und vermeiden Idealisierungen."
        }
    ],
    "Soziale Beziehungen und Interaktion": [
        {
            "frage": "K2.1 Die Unternehmensführung positioniert sich aktiv und sichtbar zugunsten flexibler Arbeitsformen.",
            "begründung": "Strategischer Rückhalt erhöht Legitimität und Verbindlichkeit für die Umsetzung im mittleren Management."
        },
        {
            "frage": "K2.2 Die Unternehmensführung kommuniziert Ziele und Nutzen flexibler Arbeit konsistent.",
            "begründung": "Klare Kommunikation der Unternehmensführung schafft Orientierung, reduziert Unsicherheiten und stärkt Akzeptanz."
        },
        {
            "frage": "K2.3 Die direkte Führungskraft unterstützt aktiv mobile und zeitflexible Arbeitsformen.",
            "begründung": "Die unmittelbare Führungskraft ist entscheidend für die Realisierung flexibler Arbeit im Alltag."
        },
        {
            "frage": "K2.4 Führungskräfte fördern aktiv Eigenverantwortung und Selbstorganisation im Team.",
            "begründung": "Selbststeuerung ist eine Schlüsselanforderung flexibler Arbeit und muss durch Führung bewusst gefördert werden."
        },
        {
            "frage": "K2.5 Führung erfolgt ergebnisorientiert statt anwesenheitsorientiert.",
            "begründung": "Leistung muss anhand von Zielerreichung bewertet werden, nicht über physische Präsenz."
        },
        {
            "frage": "K2.6 Führungskräfte sind für die Steuerung hybrider Teams qualifiziert.",
            "begründung": "Neue Arbeitsformen erfordern neue Führungskompetenzen (z. B. virtuelle Führung, asynchrone Kommunikation)."
        },
        {
            "frage": "K2.7 Die Führung etabliert verbindliche Kommunikationsstandards (z. B. Regeltermine, Rückmeldefenster).",
            "begründung": "Verlässliche Kommunikation kompensiert den Wegfall informeller Kanäle bei physischer Distanz."
        },
        {
            "frage": "K2.8 Die Teamkultur ist durch gegenseitige Unterstützung und Kooperation geprägt.",
            "begründung": "Soziale Unterstützung im Team sichert Resilienz, gerade bei geringerer physischer Präsenz."
        },
        {
            "frage": "K2.9 Es bestehen etablierte Formate für den informellen Austausch im Team.",
            "begründung": "Informelle Kommunikation stärkt soziale Bindung und Teamkohäsion."
        },
        {
            "frage": "K2.10 Die Führung fördert explizit die Vereinbarkeit von Beruf und Privatleben.",
            "begründung": "Berücksichtigung individueller Lebenslagen erhöht Motivation und senkt Belastungen."
        },
        {
            "frage": "K2.11 Teamziele sind transparent definiert und werden regelmäßig reflektiert.",
            "begründung": "Zielklarheit ist Grundlage selbstorganisierter Zusammenarbeit und kollektiver Verantwortungsübernahme."
        },
        {
            "frage": "K2.12 Beschäftigte bringen regelmäßig Vorschläge zur Verbesserung der Zusammenarbeit ein.",
            "begründung": "Partizipation fördert Identifikation mit Veränderungsprozessen und stärkt kollektives Lernen."
        },
        {
            "frage": "K2.13 Rückmeldungen zum Führungsverhalten werden regelmäßig eingeholt und berücksichtigt.",
            "begründung": "Feedback über Führung ist essenziell für Vertrauensaufbau und kontinuierliche Verbesserung der Zusammenarbeit."
        },
        {
            "frage": "K2.14 Teammitglieder kennen ihre Rollen und Verantwortlichkeiten im flexiblen Arbeitskontext.",
            "begründung": "Klar definierte Rollen erhöhen Handlungssicherheit bei geringerer persönlicher Abstimmung."
        },
        {
            "frage": "K2.15 Konflikte im Team werden frühzeitig erkannt und konstruktiv moderiert.",
            "begründung": "Konfliktlösung ist eine zentrale soziale Kompetenz, besonders relevant bei asynchroner Zusammenarbeit."
        },
        {
            "frage": "K2.16 Wertschätzung und Lob sind integraler Bestandteil der Zusammenarbeit.",
            "begründung": "Anerkennung fördert Motivation."
        },
        {
            "frage": "K2.17 Die Führung etabliert partizipative Formate zur Mitgestaltung flexibler Arbeitsprozesse.",
            "begründung": "Beteiligung erhöht Passgenauigkeit und reduziert Umsetzungsbarrieren."
        },
        {
            "frage": "K2.18 Unterschiedliche Bedürfnisse (z. B. Pflegeverantwortung, Schichtsystem) werden teamintern berücksichtigt.",
            "begründung": "Differenzierung erhöht Fairness und schafft Akzeptanz im Team."
        },
        {
            "frage": "K2.19 Die Führung fördert eine gemeinsame Wertebasis für mobiles und zeitflexibles Arbeiten.",
            "begründung": "Gemeinsame Normen und Werte stabilisieren Kooperation unter veränderten Rahmenbedingungen."
        },
        {
            "frage": "K2.20 Das Team reflektiert regelmäßig die Qualität seiner Zusammenarbeit.",
            "begründung": "Teamreflexion fördert Selbststeuerung, Offenheit und kontinuierliche Weiterentwicklung."
        }
    ]
}

# Ergebnis-Speicherung
ergebnisse = {}

# Tabs für jede Dimension inklusive Start, Abschließende Fragen und Auswertung
tab_names = ["Start"] + list(mtok_structure.keys()) + ["Abschließende Fragen"] + ["Auswertung"]
tabs = st.tabs(tab_names)

# Titelseite im Tab "Start"
with tabs[0]:
    st.title("Readiness-Check zur Einführung mobiler und zeitflexibler Arbeit")
    st.markdown("""
    Dieser Readiness-Check unterstützt Sie dabei, den betrieblichen Stand zur Einführung mobiler und zeitflexibler Arbeit systematisch zu erfassen.

    Basierend auf den vier Dimensionen des MTOK-Modells – **Mensch**, **Technik**, **Organisation** und **Kultur** – werden insgesamt neun Handlungsfelder betrachtet.
    
    In jedem Handlungsfeld beantworten Sie eine Reihe von Bewertungskriterien anhand einer standardisierten 4-Punkte-Skala:

    **Bewertungsskala:**
    - **1 = niedrig** – Das Kriterium ist kaum oder gar nicht erfüllt.
    - **2 = mittel** – Das Kriterium ist teilweise erfüllt, es bestehen Lücken oder Unsicherheiten.
    - **3 = hoch** – Das Kriterium ist weitgehend erfüllt, jedoch nicht vollständig systematisiert.
    - **4 = sehr hoch** – Das Kriterium ist vollständig erfüllt und fest im Alltag etabliert.

    Nach dem Ausfüllen aller Handlungsfelder erhalten Sie eine grafische Auswertung sowie eine indikative Zuordnung zu einem Clustertyp (z. B. *traditionell und reaktiv* oder *digital-affin und akzeptanzstark*). Ergänzend werden automatisiert passende Handlungsempfehlungen ausgesprochen.

    **Hinweis:** Die Auswertung basiert auf einer wissenschaftlichen Analyse und wurde speziell für die zerspanende Fertigung entwickelt.
    """)

# Fragen + Begründungen
for i, (dimension, felder) in enumerate(mtok_structure.items(), start=1):
    with tabs[i]:
        st.header(f"Dimension: {dimension}")
        for feld in felder:
            st.subheader(f"Handlungsfeld: {feld}")
            kriterien = Kriterien.get(feld, [])
            scores = []
            for idx, item in enumerate(kriterien):
                # Frage ohne Nummerierung
                st.markdown(f"**{item['frage']}**")
                # Begründung direkt unterhalb in grauer, kleiner Schrift
                st.markdown(f"<span style='color:gray; font-size:0.9em'>{item['begründung']}</span>", unsafe_allow_html=True)
                # Bewertungsoptionen
                score = st.radio(
                    label="Bitte bewerten:",
                    options=[1, 2, 3, 4],
                    horizontal=True,
                    key=f"{dimension}_{feld}_{idx}"
                )
                scores.append(score)
            ergebnisse[feld] = np.mean(scores) if scores else 0

with tabs[-2]:
    st.header("Abschließende Angaben")

    st.markdown("Bitte beantworten Sie die folgenden Fragen. Diese Angaben helfen bei der Interpretation der Ergebnisse und sind teilweise optional.")

    branche = st.text_input("1. In welcher Branche ist Ihr Unternehmen tätig?")

    st.markdown("2. Wie viele Mitarbeitende hat Ihr Unternehmen?")
    ma_options = ["1-9", "10-49", "50-199", "200-499", "500-1999", ">2000"]
    mitarbeitende = ""
    for option in ma_options:
        if st.checkbox(option, key=f"ma_{option}"):
            mitarbeitende = option

    st.markdown("3. In welcher Funktion sind Sie tätig?")
    funktionsbereiche = ["Geschäftsführung", "Abteilungs-/Projektleitung", "Fachexpert*in", "Mitarbeiter*in der Produktion", "Sonstige"]
    funktion = ""
    for option in funktionsbereiche:
        if st.checkbox(option, key=f"funktion_{option}"):
            funktion = option

    st.markdown("4. Wie hoch ist der Jahresumsatz Ihres Unternehmens?")
    umsatzbereiche = ["< 2 Mio. €", "2-9 Mio. €", "10-49 Mio. €", "> 50 Mio. €"]
    umsatz = ""
    for option in umsatzbereiche:
        if st.checkbox(option, key=f"umsatz_{option}"):
            umsatz = option

    st.markdown("5. In welchem der aufgeführten Bereiche würden Sie sich gerne noch weiterbilden? (optional)")
    weiterbildung = st.multiselect(
        "",
        [            "Produktentwicklung",
            "Beschaffung und Einkauf",
            "Planung und Steuerung von Produktionsabläufen",
            "Marketing",
            "Vertrieb",
            "Logistik",
            "Innerbetriebliche Verwaltung"
        ]
    )

    plz = st.text_input("6. Wo ist Ihr Unternehmen zu Hause? (Postleitzahl, optional)")

    email = st.text_input("7. Ihre E-Mail-Adresse (optional, für Ergebniszusendung):")

    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")

# Mapping der Handlungsfelder zu ihren MTOK-Dimensionen
dim_map = {
    "Produktivität und Motivation": "Mensch",
    "Persönliches Umfeld": "Mensch",
    "Arbeitsplatzgestaltung und Automatisierung": "Technik",
    "IT-Systemlandschaft und digital vernetzte Infrastruktur": "Technik",
    "Kommunikation, Kooperation und Zusammenarbeit": "Organisation",
    "Soziokulturelle und organisatorische Umwelt": "Organisation",
    "Produktionsorganisation": "Organisation",
    "Unternehmenskultur": "Kultur",
    "Soziale Beziehungen und Interaktion": "Kultur"
}

#Auswertung
with tabs[-1]:
    st.header("Auswertung")

    cluster = None

    if st.button("Radar-Diagramm anzeigen"):
        labels = [f"{feld}\n({dim_map.get(feld, '')})" for feld in ergebnisse.keys()]
        values = list(ergebnisse.values())

        if not values:
            st.warning("Bitte füllen Sie zuerst die Bewertungen in den anderen Tabs aus.")
        else:
            num_vars = len(labels)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            values_cycle = values + values[:1]
            angles_cycle = angles + angles[:1]

            fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
            ax.fill(angles_cycle, values_cycle, color='cornflowerblue', alpha=0.3)
            ax.plot(angles_cycle, values_cycle, color='royalblue', linewidth=2)
            
            ax.set_yticks([1, 2, 3, 4])
            ax.set_yticklabels(['1 = niedrig', '2', '3', '4 = sehr hoch'], fontsize=8)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=9)
            
            ax.set_title("Readiness-Profil – Mittelwerte nach Handlungsfeld", fontsize=14, pad=20)
            st.pyplot(fig)

            avg = np.mean(values)
            st.subheader("Clusterzuordnung")
            if avg >= 3.5:
                cluster = "Cluster 3 – Digital-affin und akzeptanzstark"
                st.success(f"Der Betrieb gehört wahrscheinlich zu {cluster}.")
            elif avg >= 2.8:
                cluster = "Cluster 4 – Effizient, aber strukturell gehemmt"
                st.info(f"Der Betrieb zeigt Merkmale von {cluster}.")
            elif avg >= 2.0:
                cluster = "Cluster 2 – Produktionsstark, aber mobilitätsfern"
                st.warning(f"Der Betrieb weist Charakteristika von {cluster} auf.")
            else:
                cluster = "Cluster 1 – Traditionell und reaktiv"
                st.error(f"Der Betrieb gehört vermutlich zu {cluster}.")

            # OpenAI-gestützte Handlungsempfehlung
            st.subheader("Individuelle, KI-gestützte Handlungsempfehlung")
            mitteilungen = frage_chatgpt_auswertung(ergebnisse)
            st.markdown(mitteilungen)