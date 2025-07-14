import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai # type: ignore

# API-Key aus Umgebungsvariable
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
            "frage": "M1.1 Beschäftigte wissen, welche Anforderungen mit mobiler Arbeit verbunden sind.",
            "begründung": "Mobile Arbeit erfordert Kenntnisse zu IT-Zugriff, Prozessintegration und Selbstorganisation. Unklare Regelungen führen zu Produktivitätsverlust."
        },
        {
            "frage": "M1.2 Beschäftigte wissen, welche Anforderungen mit zeitflexible Arbeit in der Fertigung verbunden sind.",
            "begründung": "Die zeitflexible Arbeit in der Zerspanung ist an technische Abläufe gebunden. Kenntnis über Konflikte (z. B. Maschinentaktung) ist Voraussetzung für realistische Umsetzung."
        },
        {
            "frage": "M1.3 Beschäftigte verfügen über die fachlichen und digitalen Kompetenzen zur Selbststeuerung.",
            "begründung": "Eigenverantwortliche Prozesskontrolle und Informationsverarbeitung sind zentrale Voraussetzungen für produktive Flexibilität."
        },
        {
            "frage": "M1.4 Beschäftigte verfügen über einen vielseitigen Aufgabenkatalog (z. B. Programmierung, Planung, Dokumentation).",
            "begründung": "Vielfältige Aufgabeninhalte fördern ein vertieftes Systemverständnis, stärken die Eigenverantwortung und erhöhen die Anschlussfähigkeit an mobile Arbeit."
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
            "frage": "M1.8 Erfahrungswissen wird dokumentiert und regelmäßig weitergegeben.",
            "begründung": "Wissenstransfer verhindert Qualitätsverluste in Teams mit wechselnden Präsenzzeiten."
        },
        {
            "frage": "M1.9 Beschäftigte erhalten gezielte Entwicklungsangebot.",
            "begründung": "Entwicklungsperspektiven erhalten Motivation und fördern langfristige Bindung."
        },
        {
            "frage": "M1.10 Beschäftigte reflektieren die Wirkung flexibler Arbeit auf ihre Produktivität.",
            "begründung": "Reflexion fördert Selbststeuerung und kontinuierliche Verbesserung – zentrale Elemente lernender Organisationen."
        }
    ],
    "Persönliches Umfeld": [
        {
            "frage": "M2.1 Beschäftigte sind offen gegenüber mobiler Arbeit.",
            "begründung": "Eine positive Grundhaltung erleichtert die Einführung digital gestützter Arbeitsformen und stärkt das Vertrauen in ortsunabhängige Lösungen."
        },
        {
            "frage": "M2.2 Beschäftigte sind offen gegenüber zeitflexibler Arbeit.",
            "begründung": "Eine positive Grundhaltung fördert Akzeptanz und Beteiligung an Flexibilisierungsprozessen im Hinblick auf Arbeitszeitgestaltung."
        },
        {
            "frage": "M2.3 Beschäftigte fühlen sich gut vorbereitet auf flexible Arbeitsgestaltungen.",
            "begründung": "Sicherheit in der Ausführung stärkt Selbstwirksamkeit und Engagement."
        },
        {
            "frage": "M2.4 Beschäftigte identifizieren sich mit ihrer Arbeit und dem Unternehemen.",
            "begründung": "Identifikation steigert Eigenverantwortung und Leistungsbereitschaft."
        },
        {
            "frage": "M2.5 Die Beschäftigten beherrschen gängige digitale Tools (z. B. E-Mail, Team-Chat, Maschineninterfaces).",
            "begründung": "Praktische Anwendungskompetenz ist Voraussetzung für effektive digitale Kollaboration."
        },
        {
            "frage": "M2.6 Beschäftigte verfügen über stabile externe Bedingungen für mobile Arbeit (z. B. Rückzugsort, soziales Umfeld).",
            "begründung": "Die Umsetzbarkeit flexibler Arbeit hängt auch von der häuslichen Situation ab."
        },
        {
            "frage": "M2.7 Beschäftigte reflektieren regelmäßig ihre Erfahrungen mit flrxiblen Arbeitsformen.",
            "begründung": "Reflexion unterstützt Lernprozesse und ermöglicht kontinuierliche Anpassung."
        },
        {
            "frage": "M2.8 Beschäftigte können Verbesserungsvorschläge zu digitalen Arbeitsmitteln aktiv einbringen.",
            "begründung": "Beteiligung an der Systemgestaltung fördert Akzeptanz und Passung."
        },
        {
            "frage": "M2.9 Beschäftigte verstehen grundlegende Funktionsweisen vernetzter digitaler Produktionssysteme.",
            "begründung": "Systemverständnis erhöht Sicherheit und reduziert Fehleranfälligkeit."
        },
    ],
    "Arbeitsplatzgestaltung und Automatisierung": [
        {
            "frage": "T1.1 Die Werkzeugmaschine ist so ausgelegt, dass sie ohne ständige Anwesenheit bedient werden kann (z. B. durch lange Laufzeiten oder automatisierte Routinetätigkeiten wie Werkstückhandling).",
            "begründung": "Eine hohe technische Selbstständigkeit der Maschine, durch Automatisierung oder durch lange unbeaufsichtigte Laufzeiten, schafft zeitliche Flexibilität und reduziert Präsenzzwang."
        },
        {
            "frage": "T1.2 Präsenzpflichtige Aufgaben (z. B. Maschineneinrichtung) können aggregiert werden.",
            "begründung": "Zusammenfassung ermöglicht planbare Präsenzzeiten und reduziert Unterbrechungen."
        },
        {
            "frage": "T1.3 Maschinenbedienung erfolgt über standardisierte und dokumentierte Arbeitsabläufe.",
            "begründung": "Standardisierung ist Grundlage für übertragbare Aufgaben, Schulung und Fernsteuerbarkeit."
        },
        {
            "frage": "T1.4 Fertigungsprozesse sind stabil und störungsarm.",
            "begründung": "Prozessstabilität ist Voraussetzung für entkoppelte Arbeit und reduziert ungeplante Eingriffe."
        },
        {
            "frage": "T1.5 Fernüberwachung und Eingriff von Fertigungsprozessen ist technisch realisiert (z. B. Kameras, Monitoring-Apps).",
            "begründung": "Visuelle und sensorische Fernkontrolle reduziert Präsenznotwendigkeit bei Routineüberwachung."
        },
        {
            "frage": "T1.6 Prüf- und Qualitätssicherungsprozesse erfolgen automatisiert oder sind entkoppelt.",
            "begründung": "Reduziert zeitliche Fixpunkte, schafft Flexibilität im Ablauf."
        },
        {
            "frage": "T1.7 Wartungsbedarfe und Eingriffsprotokolle sind digital dokumentiert und zugänglich.",
            "begründung": "Transparente Dokumentation ermöglicht Übergaben, Eigenverantwortung und hybride Betreuung."
        },
        {
            "frage": "T1.8 Echtzeitdaten zur Maschinenauslastung stehen zur Verfügung (z. B. OEE-Analyse).",
            "begründung": "Grundlage für dynamische Prozesssteuerung auch bei flexibler Anwesenheit."
        },
        {
            "frage": "T1.9 Maschinenarbeitsplätze verfügen über verlässliche Schnittstellen zu digitalen Systemen (z. B. ERP, MES).",
            "begründung": "Digitale Integration ist Grundvoraussetzung für ortsunabhängige Planung, Steuerung und Dokumentation."
        },
        {
            "frage": "T1.10 Auswirkungen flexibler Arbeit auf Produktivität und Maschinenauslastung werden systematisch erhoben.",
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
            "frage": "T2.4 Der IT-Support ist ortsunabhängig verfügbar.",
            "begründung": "Verfügbarkeit bei Problemen sichert Stabilität und erhöht Akzeptanz und Produktivität mobiler Arbeit."
        },
        {
            "frage": "T2.5 Es existieren sichere Zugriffskonzepte mit klaren Rollen und Rechten.",
            "begründung": "Klare Zugriffsrechte schützen Daten, erhöhen Vertrauen und erlauben eine skalierbare Nutzung."
        },
        {
            "frage": "T2.6 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
            "begründung": "Echtzeitintegration zwischen Bereichen ermöglicht schnelle Entscheidungen und flexible Steuerung."
        },
        {
            "frage": "T2.7 IT-Sicherheit ist systematisch für hybride Arbeitsformen geregelt.",
            "begründung": "Sicherheitskonzepte müssen mobil adaptierbar sein, um Datenrisiken zu vermeiden."
        },
        {
            "frage": "T2.8 Betriebsvereinbarungen regeln Einsatz, Nutzung und Kontrolle digitaler Systeme.",
            "begründung": "Rechtliche und organisationale Klarheit stärkt Vertrauen und verhindert Missverständnisse."
        },
        {
            "frage": "T2.9 Simulationen oder digitale Zwillinge unterstützen Planung und Steuerung der Produktion.",
            "begründung": "Vorausschauende Modellierung reduziert Planungsunsicherheiten und erhöht Reaktionsfähigkeit."
        },
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
            "frage": "O1.4 Verbindliche Regeln zur IT-Nutzung (z. B. VPN, Remote-Zugriffe) sind etabliert und bekannt.",
            "begründung": "Sicherheit und Klarheit fördern Compliance und Verlässlichkeit."
        },
        {
            "frage": "O1.5 Hybride Meetings (Präsenz und Remote) sind etabliert und technisch unterstützt.",
            "begründung": "Hybride Formate ermöglichen inklusive Zusammenarbeit bei Ortsflexibilität."
        },
        {
            "frage": "O1.6 Neue Beschäftigte werden strukturiert in Kommunikations- und Kollaborationsprozesse eingeführt.",
            "begründung": "Strukturierte Einarbeitung sichert Integration in mobile Arbeitsweisen."
        },
        {
            "frage": "O1.7 Beschäftigte wissen, welche Kanäle im Störungsfall zu nutzen sind.",
            "begründung": "Klare Kommunikationswege sichern Handlungsfähigkeit bei Abweichungen."
        },
        {
            "frage": "O1.8 Digitale Kommunikationskompetenz wird systematisch gefördert.",
            "begründung": "Mediensouveränität ist Voraussetzung für gelingende digitale Zusammenarbeit."
        },
        {
            "frage": "O1.9 Die eingesetzten digitalen Tools unterstützen die Zusammenarbeit (z. B. gemeinsame Plattformen).",
            "begründung": "Gemeinsames Arbeiten erfordert Zugriff auf zentrale Informationsressourcen."
        },
        {
            "frage": "O1.10 Bei Ziel- oder Koordinationsproblemen werden Kommunikationsstrukturen gezielt angepasst.",
            "begründung": "Lernende Kommunikation verbessert langfristig die Wirksamkeit der Kooperation."
        },
        {
            "frage": "O1.11 Die Organisation reflektiert regelmäßig die Wirkung von Zeitautonomie auf Zusammenarbeit und Kommunikation.",
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
            "frage": "O2.6 Arbeitszeitmodelle sind in Planungs- und Steuerungssysteme integriert (z. B. MES, ERP).",
            "begründung": "Nur wenn Systeme eingebunden sind, sind flexible Modelle praxistauglich und steuerbar."
        },
        {
            "frage": "O2.7 Die Aufbau- und Ablauforganisation ist anpassungsfähig (z. B. bei Sonderaufträgen oder Vertretungen).",
            "begründung": "Starre Strukturen behindern spontane Reaktion – Cluster 2/4 zeigten hier hohe Hürden."
        },
        {
            "frage": "O2.8 Verantwortung von Führung für Flexibilisierung ist definiert und implementiert.",
            "begründung": "Unklare Rollenerwartung führt zu Stillstand. Führung ist zentrale Instanz für Umsetzung und Steuerung."
        },
        {
            "frage": "O2.9 Zuständigkeiten und Vertretungen sind auch bei mobiler Arbeit eindeutig geregelt.",
            "begründung": "Klare Verantwortlichkeiten sichern Prozessstabilität und entlasten das Team."
        },
        {
            "frage": "O2.10 Feedback zur Umsetzung mobiler und zeitflexibler Arbeit wird systematisch eingeholt und genutzt.",
            "begründung": "Beteiligung der Beschäftigten stärkt Realitätsbezug und Anpassungsfähigkeit."
        },
        {
            "frage": "O2.11 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit mitgestalten.",
            "begründung": "Ein signifikanter Einfluss auf flexible Arbeitsmodelle wurde empirisch belegt."
        },
        {
            "frage": "O2.12 Pausenzeiten können im Rahmen betrieblicher Vorgaben flexibel gestaltet werden.",
            "begründung": "Autonomie über Pausen wirkt positiv auf Erholung, Effizienz und Zeitautonomie."
        }
    ],
    "Produktionsorganisation": [
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
            "frage": "O3.8 Die Produktionssteuerung erlaubt dezentrale Anpassungen durch operative Führungsebenen.",
            "begründung": "Dezentrale Steuerung erhöht Reaktionsgeschwindigkeit bei flexiblen Arbeitszeiten."
        },
        {
            "frage": "O3.9 Bei Maschinenstillstand entstehen keine unmittelbaren kritischen Produktivitätsverluste.",
            "begründung": "Die Toleranz gegenüber kurzfristiger Nichtbesetzung erlaubt mehr Zeitautonomie."
        },
        {
            "frage": "O3.10 Qualitätskontrollen sind prozessintegriert oder digital unterstützt.",
            "begründung": "Digitale Prüfprozesse ermöglichen Entkopplung von Ort und Zeit."
        },
        {
            "frage": "O3.11 Die Auftragssteuerung ist dynamisch und mit digitalen Schnittstellen vernetzt.",
            "begründung": "Echtzeitsteuerung und digitale Integration sind Grundlage für Flexibilisierung."
        },
        {
            "frage": "O3.12 Produktionsprozesse sind standardisiert dokumentiert und für andere übertragbar.",
            "begründung": "Standardisierung erhöht die Planbarkeit und Vertretbarkeit bei wechselnden Zuständigkeiten."
        },
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
            "frage": "K1.4 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
            "begründung": "Transformationsbereitschaft ist Voraussetzung für Flexibilisierung."
        },
        {
            "frage": "K1.5 Die Fehlerkultur ist konstruktiv und unterstützend.",
            "begründung": "Fehlerfreundlichkeit fördert Innovation und Lernen, besonders bei neuen Arbeitsweisen."
        },
        {
            "frage": "K1.6 Die Unternehmensführung leben Flexibilität sichtbar vor.",
            "begründung": "Vorbildfunktion der Führung prägt kulturelle Normen und Öffnung."
        },
        {
            "frage": "K1.7 Flexible Arbeit wird als Bestandteil der betrieblichen Normalität wahrgenommen.",
            "begründung": "Normalisierung senkt Widerstände und verankert Flexibilität langfristig."
        },
        {
            "frage": "K1.8 Es bestehen keine verdeckten Erwartungen an ständige Erreichbarkeit.",
            "begründung": "Entgrenzung wirkt kontraproduktiv für Work-Life-Balance und nachhaltige Nutzung."
        },
        {
            "frage": "K1.9 Unterschiedliche Arbeitsstile und Rhythmen werden akzeptiert.",
            "begründung": "Heterogenität fördert Anpassungsfähigkeit und Individualisierung."
        },
        {
            "frage": "K1.10 Mobile Arbeit wird in Teamabstimmungen berücksichtigt.",
            "begründung": "Kulturelle Integration benötigt Abstimmung und explizite Einbindung.."
        },
        {
            "frage": "K1.11 Fehler im Umgang mit neuen Arbeitsformen werden als Lernchance begriffen.",
            "begründung": "Eine konstruktive Fehlerkultur ist Voraussetzung für sichere Lernprozesse."
        },
        {
            "frage": "K1.12 Die Organisation spricht offen über Zielkonflikte zwischen Flexibilität und Produktionssicherheit.",
            "begründung": "Realistische Diskussionen fördern Vertrauen und vermeiden Idealisierungen."
        }
    ],
    "Soziale Beziehungen und Interaktion": [
        {
            "frage": "K2.1 Die Unternehmensführung positioniert sich aktiv und sichtbar zugunsten flexibler Arbeitsformen.",
            "begründung": "Strategischer Rückhalt erhöht Legitimität und Verbindlichkeit für die Umsetzung im mittleren Management."
        },
        {
            "frage": "K2.2 Die direkte Führungskraft unterstützt aktiv mobile und zeitflexible Arbeitsformen.",
            "begründung": "Die unmittelbare Führungskraft ist entscheidend für die Realisierung flexibler Arbeit im Alltag."
        },
        {
            "frage": "K2.3 Führungskräfte fördern aktiv Eigenverantwortung und Selbstorganisation im Team.",
            "begründung": "Selbststeuerung ist eine Schlüsselanforderung flexibler Arbeit und muss durch Führung bewusst gefördert werden."
        },
        {
            "frage": "K2.4 Führung erfolgt ergebnisorientiert statt anwesenheitsorientiert.",
            "begründung": "Leistung muss anhand von Zielerreichung bewertet werden, nicht über physische Präsenz."
        },
        {
            "frage": "K2.5 Führungskräfte sind für die Steuerung hybrider Teams qualifiziert.",
            "begründung": "Neue Arbeitsformen erfordern neue Führungskompetenzen (z. B. virtuelle Führung, asynchrone Kommunikation)."
        },
        {
            "frage": "K2.6 Die Führung etabliert verbindliche Kommunikationsstandards (z. B. Regeltermine, Rückmeldefenster).",
            "begründung": "Verlässliche Kommunikation kompensiert den Wegfall informeller Kanäle bei physischer Distanz."
        },
        {
            "frage": "K2.7 Die Teamkultur ist durch gegenseitige Unterstützung und Kooperation geprägt.",
            "begründung": "Soziale Unterstützung im Team sichert Resilienz, gerade bei geringerer physischer Präsenz."
        },
        {
            "frage": "K2.8 Es bestehen etablierte Formate für den informellen Austausch im Team.",
            "begründung": "Informelle Kommunikation stärkt soziale Bindung und Teamkohäsion."
        },
        {
            "frage": "K2.9 Teamziele sind transparent definiert und werden regelmäßig reflektiert.",
            "begründung": "Zielklarheit ist Grundlage selbstorganisierter Zusammenarbeit und kollektiver Verantwortungsübernahme."
        },
        {
            "frage": "K2.10 Teammitglieder kennen ihre Rollen und Verantwortlichkeiten im flexiblen Arbeitskontext.",
            "begründung": "Klar definierte Rollen erhöhen Handlungssicherheit bei geringerer persönlicher Abstimmung."
        },
        {
            "frage": "K2.11 Konflikte im Team werden frühzeitig erkannt und konstruktiv moderiert.",
            "begründung": "Konfliktlösung ist eine zentrale soziale Kompetenz, besonders relevant bei asynchroner Zusammenarbeit."
        },
        {
            "frage": "K2.12 Unterschiedliche Bedürfnisse (z. B. Pflegeverantwortung, Schichtsystem) werden teamintern berücksichtigt.",
            "begründung": "Differenzierung erhöht Fairness und schafft Akzeptanz im Team."
        },
        {
            "frage": "K2.13 Das Team reflektiert regelmäßig die Qualität seiner Zusammenarbeit.",
            "begründung": "Teamreflexion fördert Selbststeuerung, Offenheit und kontinuierliche Weiterentwicklung."
        }
    ]
}

# Mappings vorbereiten
dim_map = {feld: dim for dim, felder in mtok_structure.items() for feld in felder}

# Tabs definieren
tab_names = ["Start"] + list(mtok_structure.keys()) + ["Abschließende Fragen", "Auswertung"]

# Session-Variablen initialisieren
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0

# Navigationsbuttons
def nav_buttons(position):
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.session_state.current_tab_index > 0:
            if st.button("← Zurück", key=f"back_{position}_{st.session_state.current_tab_index}"):
                st.session_state.current_tab_index -= 1
                st.experimental_set_query_params(tab=st.session_state.current_tab_index)  # optional visuelle Navigation aktualisieren
                st.stop()
    with col3:
        if st.session_state.current_tab_index < len(tab_names) - 1:
            if st.button("Weiter →", key=f"next_{position}_{st.session_state.current_tab_index}"):
                st.session_state.current_tab_index += 1
                st.experimental_set_query_params(tab=st.session_state.current_tab_index)
                st.stop()

# Buttons oben
nav_buttons("top")

# Aktuellen Tab bestimmen
current_tab = tab_names[st.session_state.current_tab_index]

# Oben anzeigen: Dimensionstitel
st.markdown(f"###  {current_tab}")
st.markdown(" ➤ ".join([
    f"<b style='color:#1f77b4'>{name}</b>" if i == st.session_state.current_tab_index else name
    for i, name in enumerate(tab_names)
]), unsafe_allow_html=True)

# Inhalt der Tabs
if current_tab == "Start":
    st.markdown("""
    Dieser Readiness-Check unterstützt Sie dabei, den betrieblichen Stand zur Einführung mobiler und zeitflexibler Arbeit systematisch zu erfassen.
    
    Basierend auf den vier Dimensionen des MTOK-Modells – **Mensch**, **Technik**, **Organisation** und **Kultur** – werden insgesamt neun Handlungsfelder betrachtet.
    
    In jedem Handlungsfeld beantworten Sie eine Reihe von Bewertungskriterien anhand einer standardisierten 4-Punkte-Skala:
    - **1 = niedrig** – kaum erfüllt
    - **2 = mittel** – teilweise erfüllt
    - **3 = hoch** – weitgehend erfüllt
    - **4 = sehr hoch** – voll erfüllt und etabliert
    
    Nach dem Ausfüllen erhalten Sie eine grafische Auswertung und Handlungsempfehlungen.
    """)

elif current_tab in mtok_structure:
    dimension = current_tab
    for feld in mtok_structure[dimension]:
        st.subheader(f"Handlungsfeld: {feld}")
        scores = []
        for idx, item in enumerate(Kriterien.get(feld, [])):
            st.markdown(f"**{item['frage']}**")
            st.markdown(f"<span style='color:gray; font-size:0.9em'>{item['begründung']}</span>", unsafe_allow_html=True)
            score = st.radio(
                "Bitte bewerten:",
                [1, 2, 3, 4],
                horizontal=True,
                key=f"{dimension}_{feld}_{idx}"
            )
            scores.append(score)
        if scores:
            st.session_state.ergebnisse[feld] = np.mean(scores)

elif current_tab == "Abschließende Fragen":
    st.text_input("Branche", key="branche")
    st.radio("Mitarbeitende", ["1-9", "10-49", "50-199", "200-499", "500-1999", ">2000"], key="mitarbeitende")
    st.radio("Funktion", ["Geschäftsführung", "Leitung", "Fachkraft", "Produktion", "Sonstige"], key="funktion")
    st.text_input("PLZ (optional)", key="plz")
    st.text_input("E-Mail (optional)", key="email")
    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")

elif current_tab == "Auswertung":
    if st.button("Radar-Diagramm anzeigen"):
        labels = [f"{feld}\n({dim_map.get(feld, '')})" for feld in st.session_state.ergebnisse]
        values = list(st.session_state.ergebnisse.values())

        if not values:
            st.warning("Bitte zuerst alle Bewertungen ausfüllen.")
        else:
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
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

            # Clusterzuordnung
            avg = np.mean(values)
            st.subheader("Clusterzuordnung")
            if avg >= 3.5:
                cluster = "Cluster 3 – Digital-affin und akzeptanzstark"
                st.info(f"Der Betrieb gehört wahrscheinlich zu {cluster}.")
            elif avg >= 2.8:
                cluster = "Cluster 4 – Effizient, aber strukturell gehemmt"
                st.info(f"Der Betrieb zeigt Merkmale von {cluster}.")
            elif avg >= 2.0:
                cluster = "Cluster 2 – Produktionsstark, aber mobilitätsfern"
                st.info(f"Der Betrieb weist Charakteristika von {cluster} auf.")
            else:
                cluster = "Cluster 1 – Traditionell und reaktiv"
                st.info(f"Der Betrieb gehört vermutlich zu {cluster}.")

            # GPT-Auswertung
            st.subheader("Individuelle, KI-gestützte Handlungsempfehlung")

            with st.spinner("Die Handlungsempfehlungen werden generiert..."):
                antwort = frage_chatgpt_auswertung(st.session_state.ergebnisse)

            st.markdown(antwort)
           
# Trenner und Navigationsbuttons unten
st.markdown("---")
nav_buttons("bottom")
