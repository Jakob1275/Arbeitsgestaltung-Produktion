import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openai  # type: ignore
import base64
from io import BytesIO
import textwrap  # wichtig für Zeilenumbruch
import re

# API-Key aus Umgebungsvariable
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def frage_chatgpt_auswertung(ergebnisse, cluster_bezeichnung):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist arbeitswissenschaftlicher Experte für flexible Arbeit in der zerspanenden Fertigung. "
                        "Dir liegen Mittelwerte zu neun betrieblichen Handlungsfeldern sowie eine Clusterzuordnung auf Basis "
                        "einer empirischen Distanzberechnung vor. "
                        "Analysiere die Werte, erkläre das Profil des Clusters und gib priorisierte Handlungsempfehlungen.\n\n"
                        "Clusterprofile:\n"
                        "Cluster 1 – Traditionell und reaktiv: geringe Technik, hohe Unsicherheit, geringe Offenheit\n"
                        "Cluster 2 – Produktionsstark, aber mobilitätsfern: hohe Technik, geringe Offenheit und Akzeptanz\n"
                        "Cluster 3 – Digital-affin und akzeptanzstark: hohe Technik, hohe Akzeptanz, niedrige Hindernisse\n"
                        "Cluster 4 – Effizient, aber strukturell gehemmt: solide Technik, hohe Laufzeit und Komplexität, geringe Umsetzung\n\n"
                        "Deine Aufgabe:\n"
                        "1. Erkläre, warum der Fall zu dem übergebenen Cluster passt\n"
                        "2. Nenne je MTOK-Dimension (Technik, Organisation, Kultur, Mensch) 2–3 zentrale Handlungsempfehlungen\n"
                        "3. Ordne die Empfehlungen nach Relevanz (Technik zuerst, dann Organisation, Kultur, Mensch)\n\n"
                        "Formuliere kurz, prägnant und praxisnah. Verweise auf typische Merkmale des Clusters."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Die Mittelwerte der neun Handlungsfelder lauten:\n{ergebnisse}\n\n"
                        f"Der Fall wurde dem folgenden Cluster zugeordnet:\n{cluster_bezeichnung}\n\n"
                        "Bitte erkläre die Zuordnung und gib priorisierte Handlungsempfehlungen entlang des MTOK-Modells."
                    )
                }
            ]
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

# Kriterienliste
Kriterien = {
  "Produktivität und Motivation": [
    {
      "frage": "M1.1 Beschäftigte kennen die Anforderungen an mobile Arbeit.",
      "begründung": "Damit mobile Arbeit reibungslos funktioniert, müssen Beschäftigte zentrale Anforderungen wie IT-Zugänge, Prozessintegration und Selbstorganisation kennen."
    },
    {
      "frage": "M1.2 Beschäftigte kennen die Anforderungen an zeitflexible Arbeit in der Fertigung.",
      "begründung": "Nur wenn Beschäftigte die Voraussetzungen und Grenzen zeitflexibler Arbeit kennen, kann diese in der Zerspanung realistisch und störungsfrei umgesetzt werden."
    },
    {
      "frage": "M1.3 Beschäftigte verfügen über fachliche und digitale Kompetenzen zur Selbststeuerung.",
      "begründung": "Produktive flexible Arbeit erfordert eigenständige Prozesskontrolle und Informationsverarbeitung."
    },
    {
      "frage": "M1.4 Beschäftigte können gezielte Qualifizierungen zu mobilen und zeitflexiblen Arbeitsformen erhalten.",
      "begründung": "Kompetenzaufbau fördert Motivation und langfristige Bindung an flexible Arbeitsmodelle."
    },
    {
      "frage": "M1.5 Die Qualifikationsniveaus der Beschäftigten entsprechen den Anforderungen mobiler und zeitflexibler Aufgabenbearbeitung.",
      "begründung": "Eine differenzierte Qualifikationsstruktur ist zentral, um flexibel bearbeitbare Aufgaben gezielt zuzuweisen und vorhandene Potenziale effektiv zu nutzen."
    },
    {
      "frage": "M1.6 Beschäftigte können Störungen eigenständig lösen.",
      "begründung": "Flexibles Arbeiten erfordert Handlungssicherheit bei Prozessabweichungen ohne direkte Unterstützung."
    },
    {
      "frage": "M1.7 Beschäftigte können Aufgaben übernehmen, die ortsunabhängig erledigt werden können.",
      "begründung": "Ein breites Aufgabengebiet (z. B. Programmierung von CNC-Werkzeugmaschinen, Fertigungsdokumentationen) fördert Eigenverantwortung und unterstützt mobile Arbeitsformen."
    },
    {
      "frage": "M1.8 Die Arbeitsumgebung ermöglicht ein produktives Arbeiten außerhalb der Fertigung.",
      "begründung": "Ergonomische, digitale und akustische Bedingungen sichern Leistung zwischen Beschäftigten auch bei räumlicher Entkopplung."
    },
    {
      "frage": "M1.9 Flexible Arbeit wird von den Beschäftigten als Beitrag zur besseren Vereinbarkeit von Beruf und Privatleben wahrgenommen.",
      "begründung": "Eine positive Bewertung der Vereinbarkeit stärkt die intrinsische Motivation für flexible Arbeitsformen."
    }
  ],
  "Persönliches Umfeld": [
    {
      "frage": "M2.1 Beschäftigte stehen mobiler Arbeit aufgeschlossen gegenüber.",
      "begründung": "Eine positive Grundhaltung erleichtert den Einstieg in ortsunabhängiges Arbeiten."
    },
    {
      "frage": "M2.2 Beschäftigte stehen zeitflexibler Arbeit offen gegenüber.",
      "begründung": "Offenheit unterstützt die Akzeptanz variabler Arbeitszeiten."
    },
    {
      "frage": "M2.3 Beschäftigte fühlen sich gut vorbereitet auf flexible Arbeitsformen.",
      "begründung": "Vorbereitung erhöht Selbstwirksamkeit und Engagement."
    },
    {
      "frage": "M2.4 Beschäftigte identifizieren sich mit ihrer Tätigkeit und dem Unternehmen.",
      "begründung": "Hohe Identifikation stärkt Eigenverantwortung und Leistungsbereitschaft."
    },
    {
      "frage": "M2.5 Beschäftigte können aktiv Verbesserungsvorschläge einbringen.",
      "begründung": "Beteiligung fördert die Passung und Akzeptanz flexibler Konzepte (z. B. KVP-Prozess)."
    },
    {
      "frage": "M2.6 Beschäftigte beherrschen digitale Standardtools.",
      "begründung": "Digitale Anwendungskompetenz ist grundlegend für effektive Kollaboration (z. B. ERP-Software, Mailprogramm, Programmierungssoftware)."
    },
    {
      "frage": "M2.7 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren Grundfunktionen.",
      "begründung": "Systemverständnis erhöht Handlungssicherheit und reduziert Fehlbedienungen."
    },
    {
      "frage": "M2.8 Beschäftigte äußern keine grundlegenden Vorbehalte gegenüber digital vernetzten Technologien.",
      "begründung": "Technikakzeptanz ist eine zentrale Voraussetzung für Vertrauen in digitale Lösungen und mobile Prozesse."
    }
  ],
   "Arbeitsplatzgestaltung und Automatisierung": [
    {
    "frage": "T1.1 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm.",
    "begründung": "Prozessstabilität ist Voraussetzung für entkoppelte Arbeitsformen und reduziert unvorhergesehene Eingriffe bei physischer Abwesenheit."
    },
    {
    "frage": "T1.2 CNC-Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
    "begründung": "Ein hoher Automatisierungsgrad oder lange unbeaufsichtigte Laufzeiten ermöglichen zeitliche Entkopplung und reduzieren Präsenzzwänge."
    },
    {
    "frage": "T1.3 Präsenzgebundene Aufgaben (z. B. Maschineneinrichtung) können gebündelt und zeitlich verdichtet ausgeführt werden.",
    "begründung": "Planbare Präsenzphasen reduzieren Unterbrechungen und erleichtern mobile Arbeitsanteile außerhalb dieser Kernzeiten."
    },
    {
    "frage": "T1.4 Die Trennung von Programmierung und Fertigung ist prozessual und technisch möglich.",
    "begründung": "Die Trennung von Programmierung und Fertigung erlaubt ortsunabhängige Aufgabenbearbeitung, entlastet das Hallenpersonal und schafft Flexibilität. Voraussetzung sind durchgängige CAD/CAM-Systeme und eine integrierte Fertigungssteuerung."
    },
    {
    "frage": "T1.5 Prüf- und Qualitätssicherungsprozesse sind automatisiert oder organisatorisch entkoppelt.",
    "begründung": "Entkoppelte Qualitätssicherung reduziert feste Rückmeldepunkte im Prozess und ermöglicht flexiblere Zeiteinteilung."
    },
    {
    "frage": "T1.6 Produktionsprozesse sind standardisiert dokumentiert und übertragbar.",
    "begründung": "Standardisierung erleichtert Vertretungen, Übergaben und mobile Unterstützungsformate."
    },
    {
    "frage": "T1.7 Echtzeitdaten zur Maschinenauslastung sind digital verfügbar.",
    "begründung": "Prozessdaten (z. B. OEE-Analyse, Laufzeitanalyse) ermöglichen auch bei variabler Anwesenheit situationsabhängige Steuerung und Optimierung."
    },
    {
    "frage": "T1.8 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
    "begründung": "Vernetzte Systeme (z. B. ERP, MES, BDE) sind Voraussetzung für ortsunabhängige Steuerung, Planung und Dokumentation."
    },
    {
    "frage": "T1.9 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert.",
    "begründung": "Sensorische oder visuelle Fernkontrolle (z. B. Kameras, Monitoring-Apps, Maschinenzugriff) reduziert Präsenznotwendigkeit und erlaubt situatives Eingreifen."
    },
    {
    "frage": "T1.10 Methoden zur regelmäßigen Erfassung potenzieller Auswirkungen flexibler Arbeit existieren.",
    "begründung": "Systematische Erfolgskontrolle (z. B. auf Produktivität, Qualität, Maschinenauslastung) unterstützt eine kontinuierliche Verbesserung und stärkt die Legitimation flexibler Arbeitsmodelle im Produktionsbereich."
    }
   ],
   "IT-Systemlandschaft und digital vernetzte Infrastruktur": [
    {
      "frage": "T2.1 Die IT-Infrastruktur stellt geeignete mobile Endgeräte zur Verfügung.",
      "begründung": "Mobile Endgeräte (z. B. Laptops, Tablets) bilden die technische Basis für ortsunabhängiges Arbeiten in produktionsnahen Tätigkeiten.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich.",
      "begründung": "Flexibles Arbeiten erfordert sicheren Zugang (z. B. über VPN-Verbindungen) zu zentralen Anwendungen von außerhalb der Fertigung.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "T2.3 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar.",
      "begründung": "Zuverlässiger IT-Support sichert technische Funktionsfähigkeit und reduziert Akzeptanzbarrieren."
    },
    {
      "frage": "T2.4 Digitale Kommunikations- und Kollaborationstools sind standardisiert verfügbar.",
      "begründung": "Digitale Tools (z. B. MS Teams, Slack) ermöglichen dezentrale Abstimmung, Informationsaustausch und Teamkommunikation."
    },
    {
      "frage": "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
      "begründung": "Vernetzung fördert bereichsübergreifende Koordination und reduziert Medienbrüche in Echtzeitprozessen.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "T2.6 Die IT-Systeme ermöglichen ortsunabhängige Einsicht und Rückmeldungen in produktionsrelevante Echtzeitdaten.",
      "begründung": "Transparenz in Echtzeit (z. B. in Maschinenstatus, Auftragsfortschritt, Störgründe) erhöht Steuerungsfähigkeit und Flexibilität im Produktionsumfeld."
    },
    {
      "frage": "T2.7 Simulationen oder digitale Zwillinge werden zur Produktionsplanung und -steuerung eingesetzt.",
      "begründung": "Vorausschauende Modellierung verbessert Planbarkeit und Reaktionsfähigkeit im flexiblen Umfeld."
    }
    ],
    "Kommunikation, Kooperation und Zusammenarbeit": [
    {
      "frage": "O1.1 Informationen für Planung, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
      "begründung": "Ein effektiver und transparenter Informationsfluss ist die Grundlage für dezentrale Koordination, schnelle Reaktionsfähigkeit und den Ausgleich personeller Ausfälle."
    },
    {
      "frage": "O1.2 Konzepte zur systematischen Förderung digitaler Kommunikationskompetenzen und zur strukturierten Einführung neuer Beschäftigter in digitale Kooperationsprozesse existieren.",
      "begründung": "Mediensouveränität und eine fundierte Einarbeitung sind Voraussetzungen für eine funktionierende digitale Zusammenarbeit und Akzeptanz in verteilten Teams."
    },
    {
      "frage": "O1.3 Erfahrungswissen wird systematisch dokumentiert, digital zugänglich gemacht und aktiv weitergegeben.",
      "begründung": "Strukturierter Wissenstransfer (z.B. Best Practices, Lernmaterialien) sichert Qualität, fördert kontinuierliches Lernen und reduziert Abhängigkeiten von einzelnen Personen bei flexiblen Arbeitsmodellen."
    },
    {
      "frage": "O1.4 IT-Sicherheitskonzepte sind etabliert, werden regelmäßig geprüft und gewährleisten den Schutz vor externen Angriffen und Datenverlust.",
      "begründung": "Robuste IT-Sicherheitsmaßnahmen (z. B. VPN-Verbindungen) sind fundamental für den Schutz sensibler Produktions- und Unternehmensdaten und zur Aufrechterhaltung der Betriebskontinuität bei flexibler Arbeit."
    },
    {
      "frage": "O1.5 Verantwortlichkeiten für IT-Sicherheit und Datenschutz sind eindeutig definiert, und relevante Stakeholder (z.B. Betriebsrat, Datenschutzbeauftragte) sind aktiv in die Gestaltung eingebunden.",
      "begründung": "Klare Rollen und eine partizipative Einbindung relevanter Akteure fördern die Akzeptanz, gewährleisten die Einhaltung rechtlicher Rahmenbedingungen und stärken die Governance-Struktur."
    },
    {
      "frage": "O1.6 Es können digitale und hybride Formate zum sozialen Austausch und Teambuilding eingeführt werden.",
      "begründung": "Die Qualität des informellen Austauschs (z.B. virtuelle Kaffeepausen, regelmäßige Team-Events) ist entscheidend für den Teamzusammenhalt und die Vermeidung von Isolation bei mobiler Arbeit."
    }
    ],
    "Soziokulturelle und organisatorische Umwelt": [
    {
      "frage": "O2.1 Der Betrieb verfügt über ausreichend qualifizierte Fachkräfte in der zerspanenden Fertigung.",
      "begründung": "Fachkräftesicherung ist die Grundlage produktiver Flexibilisierung. Ohne entsprechende Qualifikation scheitern mobile und zeitflexible Modelle bereits in der Umsetzung."
    },
    {
      "frage": "O2.2 Kenntnisse über relevante rechtliche Rahmenbedingungen sind vorhanden und können in die Planung flexibler Arbeitsformen einfließen.",
      "begründung": "Rechtskonformität (z. B. Arbeitszeitgesetz, Datenschutz) erhöht die Akzeptanz flexibler Arbeit und verhindert Unsicherheiten oder Fehlentwicklungen."
    },
    {
      "frage": "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und zeitflexibler Arbeit.",
      "begründung": "Klare Regelungen schaffen Rechtssicherheit und Orientierung.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.4 Potenzielle externe Anforderungen von Kunden, Lieferanten oder Partnern können in eine Flexibilitätsstrategie einbezogen werden.",
      "begründung": "Schnittstellen zu externen Akteuren müssen abgestimmt sein, damit flexible Arbeitsformen betrieblich und marktseitig umsetzbar sind."
    },
    {
      "frage": "O2.5 Die Personalplanung berücksichtigt flexible Zeiten und -orte und ist technisch im Planungssystem abbildbar.",
      "begründung": "Flexible Arbeitsmodelle erfordern sowohl organisatorische Offenheit als auch die technische Integration in Systeme wie MES oder ERP. Nur wenn beides gegeben ist, können Einsätze verlässlich geplant, gesteuert und dokumentiert werden.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.6 Die Fertigungsstrukturen und -prozesse sind anpassungsfähig.",
      "begründung": "Strukturelle Anpassungsfähigkeit (z. B. bei Sonderaufträgen oder kurzfristigen Vertretungen) ist Voraussetzung für spontane Reaktion und produktive Umsetzung von Flexibilität."
    },
    {
      "frage": "O2.7 Verantwortlichkeiten für die Einführung und den operativen Alltag flexibler Arbeitsformen können klar geregelt werden.",
      "begründung": "Sowohl strategische Verantwortlichkeiten zur Einführung als auch klare operative Zuständigkeiten und Vertretungsregelungen sind notwendig, um flexible Arbeit erfolgreich und stabil umzusetzen."
    },
    {
      "frage": "O2.8 Die wirtschaftlichen Auswirkungen flexibler Arbeitsformen werden im Unternehmen systematisch bewertet.",
      "begründung": "Eine fundierte ökonomische Analyse, etwa zu Investitionen, Prozessoptimierungen und Folgekosten, ist entscheidend für die strategische Legitimation und nachhaltige Einführung flexibler Arbeitsmodelle."
    },
    {
      "frage": "O2.9 Prozesse zur regelmäßigen Erfassung und Nutzung von Rückmeldungen zur flexiblen Arbeitsgestaltung existieren oder können etabliert werden.",
      "begründung": "Systematisches Feedback stärkt die Passung und ermöglicht lernorientierte Anpassungen der Flexibilisierungsstrategie."
    },
    {
      "frage": "O2.10 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten.",
      "begründung": "Die Möglichkeit zur Mitgestaltung ist empirisch als signifikanter Einflussfaktor für erfolgreiche Flexibilisierung belegt."
    },
    {
      "frage": "O2.11 Pausen können im Rahmen betrieblicher Vorgaben flexibel genommen werden.",
      "begründung": "Zeitliche Autonomie bei Pausen erhöht Erholungseffekte, unterstützt eigenverantwortliche Taktung und stärkt die Selbstbestimmung im Arbeitsprozess."
    },
    {
      "frage": "O2.12 Arbeitszeitkonten oder vergleichbare Instrumente werden aktiv zur Steuerung flexibler Arbeitszeiten genutzt.",
      "begründung": "Geeignete Systeme sichern Transparenz, vermeiden inoffizielle Konten und fördern eine faire Nutzung flexibler Arbeitsmodelle.",
      "einschraenkung": "1_und_4"
    }
    ],
    "Produktionsorganisation": [
    {
    "frage": "O3.1 Die Aufgaben sind hinsichtlich ihrer Präsenzbindung analysiert und systematisch aufteilbar.",
      "begründung": "Eine differenzierte Analyse präsenzpflichtiger und mobil bearbeitbarer Tätigkeiten ist Grundlage für jede flexible Arbeitsgestaltung (z. B. Trennung von Vorbereitung, Rüsten, Fertigen, Prüfen)."
    },
    {
    "frage": "O3.2 Die durchschnittliche Losgröße erlaubt kurzfristige Umplanungen.",
      "begründung": "Kleinere Losgrößen erhöhen die Dispositionsfreiheit und ermöglichen flexiblere Einsatzzeiten – empirisch als förderlich identifiziert."
    },
    {
    "frage": "O3.3 Lauf- und Durchlaufzeiten sind planbar und stabil steuerbar.",
      "begründung": "Stabile Prozesszeiten schaffen Handlungssicherheit für mobile oder zeitlich entkoppelte Einsätze."
    },
    {
    "frage": "O3.4 Die Produktionsplanung ist mit flexiblen Arbeitszeitmodellen kompatibel.",
      "begründung": "Eine Planung, die unterschiedliche Anwesenheitszeiten berücksichtigt, ist Voraussetzung für flexible Arbeitsgestaltung."
    },
    {
    "frage": "O3.5 Die Schicht- und Einsatzplanung ist dynamisch anpassbar.",
      "begründung": "Starre Schichtsysteme schränken Flexibilität ein. Dynamik ermöglicht individuelle Gestaltungsspielräume."
    },
    {
    "frage": "O3.6 Die Planung von personellen Puffern zur Kompensation von Engpässen ist möglich.",
      "begründung": "Ausweichkapazitäten sind essenziell, um individuelle Flexibilität ohne Produktivitätsverlust zu ermöglichen."
    },
    {
      "frage": "O3.7 Rüstprozesse sind kurz, standardisiert und in die Planung integriert.",
      "begründung": "Effiziente Rüstprozesse erhöhen die Steuerbarkeit und Reaktionsgeschwindigkeit bei flexiblen Arbeitszeiten."
    },
    {
      "frage": "O3.8 Qualitätskontrollen sind prozessintegriert oder digital unterstützt.",
      "begründung": "Die Integration in den Prozessverlauf oder digitale Unterstützung ermöglichen entkoppelte Kontrollmechanismen."
    },
    {
      "frage": "O3.9 Operative Führungskräfte können dezentral Anpassungen in der Steuerung vornehmen.",
      "begründung": "Dezentrale Entscheidungskompetenz erhöht Reaktionsfähigkeit bei sich ändernden Anwesenheiten und Aufgabenverteilungen."
    },
    {
      "frage": "O3.10 Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten.",
      "begründung": "Toleranz gegenüber kurzfristiger Abwesenheit eröffnet Möglichkeiten für zeitautonome Arbeitsgestaltung."
    },
    {
      "frage": "O3.11 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
      "begründung": "Digitale Vernetzung und Flexibilität der Steuerung ermöglichen schnelle Reaktionen auf sich ändernde Rahmenbedingungen."
    }
    ],
    "Unternehmenskultur": [
    {
    "frage": "K1.1 Im Unternehmen wird Vertrauen als Grundlage der Zusammenarbeit gelebt.",
      "begründung": "Vertrauen ist elementar für mobile und zeitflexible Arbeit, da Kontrolle nicht über physische Präsenz erfolgen kann.",
      "einschraenkung": "1_und_4"
    },
    {
    "frage": "K1.2 Beschäftigte erhalten Handlungsfreiräume zur Gestaltung ihrer Arbeit.",
      "begründung": "Handlungsspielräume fördern Motivation, Eigenverantwortung und Innovationspotenzial, welche zentrale Voraussetzungen für flexible Arbeit sind."
    },
    {
    "frage": "K1.3 Zielerreichung hat Vorrang vor physischer Anwesenheit.",
      "begründung": "Ergebnisorientierung statt Präsenzkultur stärkt Flexibilisierung und Leistungsfokus.",
        "einschraenkung": "1_und_4"
    },
    {
    "frage": "K1.4 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
      "begründung": "Akzeptanz und Offenheit gegenüber Veränderung sind kulturelle Grundlagen flexibler Arbeitsgestaltung."
    },
    {
      "frage": "K1.5 Fehler im Umgang mit neuen Arbeitsformen werden offen thematisiert und als Lernchance genutzt.",
      "begründung": "Eine konstruktive Fehlerkultur fördert Anpassungsfähigkeit, Lernprozesse und Innovationskraft bei der Einführung flexibler Modelle."
    },
    {
      "frage": "K1.6 Es bestehen keine verdeckten Erwartungen an ständige Erreichbarkeit.",
      "begründung": "Kulturelle Entgrenzung gefährdet Erholung, Selbststeuerung und nachhaltige Nutzung flexibler Arbeitsformen.",
        "einschraenkung": "1_und_4"
    },
    {
      "frage": "K1.7 Möglichkeiten zur systematischen Integration mobiler Arbeit in Teamabstimmungen existieren oder können geschaffen werden.",
      "begründung": "Kulturelle Integration erfordert explizite Berücksichtigung dezentraler Arbeit in Kommunikationsprozesse."
    },
    {
      "frage": "K1.8 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
      "begründung": "Transparente Diskussion über Zielkonflikte stärkt Vertrauen und vermeidet dysfunktionale Idealisierungen."
    },
    {
      "frage": "K1.9 Prozesse zur systematischen Erfassung und Reflexion potenzieller kultureller Barrieren bei der Einführung flexibler Arbeit existieren oder sind planbar.",
      "begründung": "Nur durch strukturiertes Feedback lassen sich kulturelle Hürden identifizieren und gezielt adressieren."
    }
    ],
   "Soziale Beziehungen und Interaktion": [
    {
      "frage": "K2.1 Die Unternehmensführung positioniert sich aktiv und lebt Flexibilität sichtbar vor.",
      "begründung": "Ein strategisch sichtbares Vorleben erhöht die Legitimität flexibler Arbeit und schafft Orientierung für nachgelagerte Führungsebenen.",
        "einschraenkung": "1_und_4"
    },
    {
      "frage": "K2.2 Führungskräfte unterstützen aktiv flexible Arbeitsformen und fördern Eigenverantwortung im Team.",
      "begründung": "Erfolgreiche flexible Arbeit erfordert sowohl strukturelle Unterstützung durch die Führung als auch eine gezielte Förderung von Selbstorganisation und Eigenverantwortung im Team."
    },
    {
      "frage": "K2.3 Führungskräfte verfügen über Kompetenzen zur Steuerung hybrider Teams.",
      "begründung": "Hybride Arbeit stellt neue Anforderungen an Führung, insbesondere im Umgang mit virtueller Kommunikation und dezentraler Koordination."
    },
    {
      "frage": "K2.4 Die Teamkultur ist durch gegenseitige Unterstützung und Kooperation geprägt.",
      "begründung": "Soziale Unterstützung erhöht Resilienz, welches ein zentraler Erfolgsfaktor bei reduzierter Präsenz ist."
    },
    {
      "frage": "K2.5 Es bestehen etablierte Formate für den informellen Austausch im Team.",
      "begründung": "Informelle Kommunikation fördert Vertrauen und Zusammenhalt.",
        "einschraenkung": "1_und_4"
    },
    {
      "frage": "K2.6 Teamziele und die Qualität der Zusammenarbeit werden regelmäßig reflektiert und angepasst.",
      "begründung": "Gemeinsame Reflexion stärkt Selbststeuerung und fördert kontinuierliche Weiterentwicklung."
    },
    {
      "frage": "K2.7 Teammitglieder kennen ihre Rollen und Verantwortlichkeiten.",
      "begründung": "Klare Rollenklarheit erhöht Handlungssicherheit und reduziert Koordinationsaufwand."
    },
    {
      "frage": "K2.8 Konflikte im Team werden frühzeitig erkannt und konstruktiv moderiert.",
      "begründung": "Konstruktiver Umgang mit Konflikten ist in asynchronen oder hybriden Teams besonders relevant."
    },
    {
      "frage": "K2.9 Unterschiedliche Arbeitsstile und -rhythmen werden anerkannt und integriert.",
      "begründung": "Individuelle Arbeitsstile zu integrieren, erhöht die Flexibilität und fördert effektive Teamarbeit."
    }
  ]
    }

# --- Hilfsfunktionen ---
def categorize_cnc_machines(num_machines_raw):
    if num_machines_raw is None:
        return np.nan
    mapping = {
        "< 5": 1,
        "5-10": 2,
        "11-24": 3,
        "≥ 25": 4
    }
    return mapping.get(num_machines_raw, np.nan)
    
def categorize_automation_percentage(percentage_str):
    if percentage_str is None:
        return np.nan
    mapping = {
        "0%": 1,
        "1-25%": 2,
        "26-49%": 3,
        "≥ 50%": 4
    }
    return mapping.get(percentage_str, np.nan)

def categorize_losgroesse(losgroesse_str):
    mapping = {
        "< 5": 1,
        "5-50": 2,
        "51-99": 3,
        "≥ 100": 4
    }
    return mapping.get(losgroesse_str, np.nan)

def categorize_durchlaufzeit(durchlaufzeit_str):
    mapping = {
        "< 10 min": 1,
        "11–30 min": 2,
        "31–89 min": 3,
        "≥ 90 min": 4
    }
    return mapping.get(durchlaufzeit_str, np.nan)

def categorize_laufzeit(laufzeit_str):
    mapping = {
        "< 1 Tag": 1,
        "1–3 Tage": 2,
        "4–6 Tage": 3,
        "≥ 7 Tage": 4
    }
    return mapping.get(laufzeit_str, np.nan)

kriterien_item_to_cluster_variable_mapping = {
       
    # 1. Automatisierungsgrad (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 2. Anzahl CNC-Werkzeugmaschinen (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 3. Losgröße (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 4. Durchlaufzeit (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 5. Laufzeit (Wert kommt direkt aus der "Abschließende Fragen" Sektion)

    # Diese 5 Variablen werden direkt abgefragt und müssen hier NICHT gemappt werden.
    # Ihre Werte werden in berechne_clusterzuordnung separat verarbeitet.

    # 6. Digitalisierungsgrad
    "Digitalisierungsgrad": [
        "M2.7 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren Grundfunktionen.",
        "T1.8 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
        "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
        "T2.6 Die IT-Systeme ermöglichen ortsunabhängige Einsicht und Rückmeldungen in produktionsrelevante Echtzeitdaten.",
        "T2.7 Simulationen oder digitale Zwillinge werden zur Produktionsplanung und -steuerung eingesetzt.",
        "O2.6 Die Personalplanung berücksichtigt flexible Zeiten und -orte und ist technisch im Planungssystem abbildbar.",
        "O3.11 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar."
    ],
    
    # 7. Prozessinstabilität
    "Prozessinstabilität": [
        "T1.1 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm.", # Niedriger Wert hier bedeutet hohe Instabilität (daher Skala invertiert für dieses Item bei Berechnung)
        "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
        "O1.2 Konzepte zur systematischen Förderung digitaler Kommunikationskompetenzen und zur strukturierten Einführung neuer Beschäftigter in digitale Kooperationsprozesse existieren.",
        "O3.10 Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten.",
    ],
    
    # 8. Nutzen (Wahrgenommener Nutzen von Flexibilität)
    "Nutzen": [
        "T1.10 Methoden zur regelmäßigen Erfassung potenzieller Auswirkungen flexibler Arbeit existieren.",
        "K1.3 Zielerreichung hat Vorrang vor physischer Anwesenheit.",
        "K1.4 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
        "K1.8 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
        "K2.2 Führungskräfte unterstützen aktiv flexible Arbeitsformen und fördern Eigenverantwortung im Team."
    ],
    
    # 9. Akzeptanz
    "Akzeptanz": [
        "M1.9 Flexible Arbeit wird von den Beschäftigten als Beitrag zur besseren Vereinbarkeit von Beruf und Privatleben wahrgenommen.",
        "M2.1 Beschäftigte stehen mobiler Arbeit aufgeschlossen gegenüber.",
        "M2.2 Beschäftigte stehen zeitflexibler Arbeit offen gegenüber.",
        "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und zeitflexibler Arbeit.",
        "O2.9 Prozesse zur regelmäßigen Erfassung und Nutzung von Rückmeldungen zur flexiblen Arbeitsgestaltung existieren oder können etabliert werden.",
        "K1.4 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
        "K1.8 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
        "K2.1 Die Unternehmensführung positioniert sich aktiv und lebt Flexibilität sichtbar vor."
    ],
    
    # 10. Aufwand Zeit (Wahrgenommener Zeitaufwand für flexible Arbeit)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Score der zugewiesenen Fragen INVERTIERT,
    # da ein HOHEr Score in der Frage ("können mitgestalten") einen NIEDRIGEN "Aufwand Zeit" für das Cluster bedeutet.
    "Aufwand Zeit": [
        "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
        "O1.4 IT-Sicherheitskonzepte sind etabliert, werden regelmäßig geprüft und gewährleisten den Schutz vor externen Angriffen und Datenverlust.",
        "O2.10 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten.",
        "O3.4 Die Produktionsplanung ist mit flexiblen Arbeitszeitmodellen kompatibel.",
        "O3.5 Die Schicht- und Einsatzplanung ist dynamisch anpassbar."
    ],
    
    # 11. Aufwand Mobil (Wahrgenommener Aufwand für mobiles Arbeiten)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Score der zugewiesenen Fragen INVERTIERT,
    # da ein HOHEr Score in der Frage ("Arbeitsumgebung ermöglicht") einen NIEDRIGEN "Aufwand Mobil" für das Cluster bedeutet.
    "Aufwand Mobil": [
        "M1.8 Die Arbeitsumgebung ermöglicht ein produktives Arbeiten außerhalb der Fertigung.",
        "M2.1 Beschäftigte stehen mobiler Arbeit aufgeschlossen gegenüber.",
        "T1.1 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm.",
        "T1.2 CNC-Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "T1.4 Die Trennung von Programmierung und Fertigung ist prozessual und technisch möglich.",
        "T1.9 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert.",
        "T2.3 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar.",
        "O1.5 Verantwortlichkeiten für IT-Sicherheit und Datenschutz sind eindeutig definiert, und relevante Stakeholder (z.B. Betriebsrat, Datenschutzbeauftragte) sind aktiv in die Gestaltung eingebunden."
        
    ]
}


# Clusterprofile aus empirischer Clustertabelle (WERTE GENAU ÜBERNEHMEN!)
# Die 'Variable' Namen aus der Tabelle des Nutzers sind hier die Keys
cluster_item_values = {
    "Cluster 1 – Traditionell und reaktiv": {
        "Automatisierungsgrad": 2,
        "Anzahl CNC-Werkzeugmaschinen": 2,
        "Losgröße": 2,
        "Durchlaufzeit": 2,
        "Laufzeit": 2,
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 3, # Hohe Instabilität
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3, # Hoher Aufwand (im Clusterprofil)
        "Aufwand Mobil": 4 # Hoher Aufwand (im Clusterprofil)
    },
    "Cluster 2 – Effizient, aber nicht flexibel": {
        "Automatisierungsgrad": 3,
        "Anzahl CNC-Werkzeugmaschinen": 3,
        "Losgröße": 4,
        "Durchlaufzeit": 3,
        "Laufzeit": 1, # Niedrige Laufzeit (geringe unbeaufsichtigte Zeit)
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 2,
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3,
        "Aufwand Mobil": 4
    },
    "Cluster 3 – Digital-affin und akzeptanzstark": {
        "Automatisierungsgrad": 4,
        "Anzahl CNC-Werkzeugmaschinen": 2, # Beispielwert; hier wird nun der Wert aus der st.number_input Kategorisierung landen
        "Losgröße": 2,
        "Durchlaufzeit": 2,
        "Laufzeit": 2,
        "Digitalisierungsgrad": 3,
        "Prozessinstabilität": 2,
        "Nutzen": 3,
        "Akzeptanz": 3,
        "Aufwand Zeit": 2,
        "Aufwand Mobil": 3
    },
    "Cluster 4 – Effizient, aber strukturell gehemmt": {
        "Automatisierungsgrad": 2,
        "Anzahl CNC-Werkzeugmaschinen": 3, # Beispielwert; hier wird nun der Wert aus der st.number_input Kategorisierung landen
        "Losgröße": 2,
        "Durchlaufzeit": 4, # Hohe Durchlaufzeit
        "Laufzeit": 3, # Hohe Laufzeit
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 2,
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3,
        "Aufwand Mobil": 3
    }
}

#Berechnung
def berechne_clusterzuordnung(kriterien_all_items_dict):
    # 1. Sammle alle individuellen Item-Bewertungen aus dem item_to_radio_key_map
    all_item_scores_flat = {}
    item_to_radio_key_map = st.session_state.get("item_to_radio_key_map", {})

    for frage_text, session_key in item_to_radio_key_map.items():
        if session_key in st.session_state and st.session_state[session_key] is not None:
            all_item_scores_flat[frage_text] = st.session_state[session_key]
    
    # 2. Berechne die Werte für die 11 spezifischen Cluster-Variablen des Nutzers
    nutzer_cluster_variable_werte = {}

    direct_input_keys = {
        "Anzahl CNC-Werkzeugmaschinen": ("cnc_range", "anzahl_cnc_werkzeugmaschinen_categorized", categorize_cnc_machines),
        "Automatisierungsgrad": ("automation_range", "automatisierungsgrad_categorized", categorize_automation_percentage),
        "Losgröße": ("losgroesse_range", "losgroesse_categorized", categorize_losgroesse),
        "Durchlaufzeit": ("durchlaufzeit_range", "durchlaufzeit_categorized", categorize_durchlaufzeit),
        "Laufzeit": ("laufzeit_range", "laufzeit_categorized", categorize_laufzeit)
    }

    direct_input_vars = list(direct_input_keys.keys())

    for var_name, (range_key, categorized_key, categorize_func) in direct_input_keys.items():
        # Falls noch nicht kategorisiert: nachträglich kategorisieren
        if categorized_key not in st.session_state:
            st.session_state[categorized_key] = categorize_func(st.session_state.get(range_key))

        value = st.session_state.get(categorized_key, float('nan'))
        if isinstance(value, (int, float)) and not np.isnan(value):
            nutzer_cluster_variable_werte[var_name] = value
        else:
            nutzer_cluster_variable_werte[var_name] = float('nan')

    # Behandlung der restlichen Variablen, die aus Kriterien-Items gemappt werden
    for cluster_var_name, associated_item_questions in kriterien_item_to_cluster_variable_mapping.items():
        if cluster_var_name not in direct_input_vars:
            scores_for_variable = []
            for q_text in associated_item_questions:
                if q_text in all_item_scores_flat:
                    scores_for_variable.append(all_item_scores_flat[q_text])

            if scores_for_variable:
                calculated_score = np.mean(scores_for_variable)

                # Invertierung
                if cluster_var_name in ["Aufwand Zeit", "Aufwand Mobil", "Prozessinstabilität"]:
                    nutzer_cluster_variable_werte[cluster_var_name] = 5 - calculated_score
                else:
                    nutzer_cluster_variable_werte[cluster_var_name] = calculated_score
            else:
                nutzer_cluster_variable_werte[cluster_var_name] = float('nan')

    # Filter NaN-Werte
    nutzer_cluster_variable_werte_filtered = {k: v for k, v in nutzer_cluster_variable_werte.items() if not np.isnan(v)}

    if not nutzer_cluster_variable_werte_filtered:
        return "Bitte bewerten Sie genügend Kriterien für die Clusterzuordnung (einschließlich der direkten Abfragen).", {}

    # Mindestanzahl an bewerteten Variablen
    MIN_CLUSTER_VARS_SCORED = 7
    if len(nutzer_cluster_variable_werte_filtered) < MIN_CLUSTER_VARS_SCORED:
        return f"Bitte bewerten Sie mindestens {MIN_CLUSTER_VARS_SCORED} relevante Kriterien-Sets (Cluster-Variablen) für eine präzise Clusterzuordnung. Aktuell sind {len(nutzer_cluster_variable_werte_filtered)} bewertet.", {}

    # Abweichungen berechnen
    abweichungen = {}
    for cluster_name, cluster_profil_werte in cluster_item_values.items():
        diffs = []
        for cluster_var_name, nutzer_wert in nutzer_cluster_variable_werte_filtered.items():
            if cluster_var_name in cluster_profil_werte:
                diffs.append(abs(nutzer_wert - cluster_profil_werte[cluster_var_name]))
        abweichungen[cluster_name] = np.mean(diffs) if diffs else float('inf')

    if not abweichungen or all(v == float('inf') for v in abweichungen.values()):
        return "Keine passende Clusterzuordnung möglich, bitte mehr Kriterien in relevanten Bereichen bewerten.", {}

    bestes_cluster = min(abweichungen, key=abweichungen.get)
    return bestes_cluster, abweichungen

# --- Ende der Berechnungslogik ---

# --- Start des Streamlit UI Codes ---
# Initialisierung der Session State Variablen vor der UI-Logik
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0

if "ergebnisse" not in st.session_state:
    st.session_state.ergebnisse = {}

# CNC-Maschinen (feste Kategorien via st.radio)
if "cnc_range" not in st.session_state:
    st.session_state.cnc_range = None
if "anzahl_cnc_werkzeugmaschinen_categorized" not in st.session_state:
    st.session_state.anzahl_cnc_werkzeugmaschinen_categorized = categorize_cnc_machines(st.session_state.cnc_range)

if "automation_range" not in st.session_state:
    st.session_state.automation_range = None
if "automatisierungsgrad_categorized" not in st.session_state:
    st.session_state.automatisierungsgrad_categorized = categorize_automation_percentage(st.session_state.automation_range)

if "losgroesse_range" not in st.session_state:
    st.session_state.losgroesse_range = None
if "losgroesse_categorized" not in st.session_state:
    st.session_state.losgroesse_categorized = categorize_losgroesse(st.session_state.losgroesse_range)

if "durchlaufzeit_range" not in st.session_state:
    st.session_state.durchlaufzeit_range = None
if "durchlaufzeit_categorized" not in st.session_state:
    st.session_state.durchlaufzeit_categorized = categorize_durchlaufzeit(st.session_state.durchlaufzeit_range)

if "laufzeit_range" not in st.session_state:
    st.session_state.laufzeit_range = None
if "laufzeit_categorized" not in st.session_state:
    st.session_state.laufzeit_categorized = categorize_laufzeit(st.session_state.laufzeit_range)

# Allgemeine Angaben
if 'branche_input' not in st.session_state:
    st.session_state.branche_input = ""
if 'mitarbeitende_radio' not in st.session_state:
    st.session_state.mitarbeitende_radio = None
if 'funktion_radio' not in st.session_state:
    st.session_state.funktion_radio = None
if 'plz_input' not in st.session_state:
    st.session_state.plz_input = ""
if 'email_input' not in st.session_state:
    st.session_state.email_input = ""


# Navigationsbuttons
def nav_buttons(position):
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.session_state.current_tab_index > 0:
            if st.button("← Zurück", key=f"back_{position}"):
                st.session_state.current_tab_index -= 1
                st.rerun()
    with col3:
        if st.session_state.current_tab_index < len(tab_names) - 1:
            if st.button("Weiter →", key=f"next_{position}"):
                st.session_state.current_tab_index += 1
                st.rerun()

# Tabs definieren
tab_names = ["Start"] + list(mtok_structure.keys()) + ["Abschließende Fragen", "Auswertung"]

# Scroll-Anker oben
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# Oben: Navigation anzeigen
nav_buttons("top")

# Aktuellen Tab bestimmen
current_tab = tab_names[st.session_state.current_tab_index]
st.markdown(f"## {current_tab}")
st.markdown(" ➤ ".join([
    f"<b style='color:#1f77b4'>{name}</b>" if name == current_tab else name
    for name in tab_names
]), unsafe_allow_html=True)

# Inhalt der Tabs
if current_tab == "Start":
    st.markdown("""
        Dieser **Readiness-Check** wurde konzipiert, um Unternehmen der **zerspanenden Fertigung** einen systematischen Weg zur Bewertung ihres aktuellen Reifegrads für die Einführung und erfolgreiche Implementierung **mobiler und zeitflexibler Arbeitsgestaltungen** aufzuzeigen.

        In einer Zeit beschleunigter Digitalisierung und sich wandelnder Arbeitsmodelle stellt sich die Frage nach der optimalen Gestaltung von Präsenz und Flexibilität. Dieses Tool bietet Ihnen eine präzise Standortbestimmung und leitet Sie durch die komplexen Anforderungen dieser Transformation.

        Dieses Modell basiert auf den vier integralen arbeitswissenschaftlichen Gestaltungsdimensionen des **MTOK-Modells** – **Mensch**, **Technik**, **Organisation** und **Kultur**. Es differenziert diese in **neun empirisch fundierte Handlungsfelder**, deren Kriterien speziell auf die Besonderheiten der zerspanenden Fertigung zugeschnitten sind.

        Für jedes Kriterium bewerten Sie den aktuellen Zustand Ihres Betriebs auf einer standardisierten **4-Punkte-Skala**:

        * **1 = Niedrig:** Das Kriterium ist aktuell nicht erfüllt.
        * **2 = Mittel:** Erste Ansätze sind erkennbar, aber das Kriterium ist nur in Ansätzen erfüllt.
        * **3 = Hoch:** Das Kriterium ist weitgehend umgesetzt und eine solide Grundlage ist vorhanden.
        * **4 = Sehr hoch:** Das Kriterium ist vollständig umgesetzt und fest im Betrieb etabliert.

        Nach Abschluss der Bewertung erhalten Sie ein **individuelles grafisches Readiness-Profil**, das Ihre Stärken und Potenziale aufzeigt. Darauf aufbauend generiert das System **maßgeschneiderte Handlungsempfehlungen**, die Ihnen konkrete Schritte zur Weiterentwicklung Ihrer flexiblen Arbeitsgestaltung auf Basis empirisch hergeleiteter Clusters aufzeigen.
        """)

elif current_tab in mtok_structure:
    dimension = current_tab
    for feld in mtok_structure[dimension]:
        st.subheader(f"Handlungsfeld: {feld}")
        scores_for_this_hf = []

        for idx, item in enumerate(Kriterien.get(feld, [])):
            frage_text = item["frage"]
            begruendung = item["begründung"]

            st.markdown(f"**{frage_text}**")
            st.markdown(f"<span style='color:gray; font-size:0.9em'>{begruendung}</span>", unsafe_allow_html=True)

            # Nutze indexbasierten Schlüssel (idx), damit die Zuordnung mit Kriterien stabil bleibt
            radio_key = f"{dimension}_{feld}_{idx}"

            # Mapping zur späteren Auswertung
            if "item_to_radio_key_map" not in st.session_state:
                st.session_state["item_to_radio_key_map"] = {}
            st.session_state["item_to_radio_key_map"][item['frage']] = f"{radio_key}_score"
            score_key = f"{radio_key}_score"

            # Bewertungsoptionen abhängig von Einschränkung
            einschraenkung = item.get("einschraenkung", None)
            if einschraenkung == "1_und_4":
                options = [1, 4]
            else:
                options = [1, 2, 3, 4]

            # Hole ggf. vorhandenen Wert
            initial_value = st.session_state.get(score_key, None)

            # Bestimme Default-Wert, wenn vorhanden
            try:
                default_index = options.index(initial_value) if initial_value is not None else 0
            except ValueError:
                default_index = 0

            # Bewertungsauswahl anzeigen
            score = st.radio(
                "Bitte bewerten:",
                options,
                horizontal=True,
                key=radio_key,
                index=default_index
            )

            # Speichere Score separat (mit _score-Endung)
            if score is not None:
                st.session_state[score_key] = score
                scores_for_this_hf.append(score)
            else:
                scores_for_this_hf.append(np.nan)

        # Mittelwert für dieses Handlungsfeld speichern
        if any(~np.isnan(scores_for_this_hf)):
            st.session_state.ergebnisse[feld] = np.nanmean(scores_for_this_hf)
        elif feld in st.session_state.ergebnisse:
            del st.session_state.ergebnisse[feld]

elif current_tab == "Abschließende Fragen":
    st.text_input("Branche", key="branche_input") 
    st.radio(
    "Wie viele Mitarbeitende arbeiten in Ihrem Unternehmen?",
    ["1-9", "10-49", "50-199", "200-499", "500-1999", "≥2000"],
    index=None,
    key="mitarbeitende_radio_input"
    )
    st.radio(
    "In welcher Funktion sind Sie in Ihrem Unternehmen tätig?",
    ["Geschäftsführer", "Produktions-/ Fertigungsleitung", "Arbeitsvorbereitung", "Teamleitung", "Planungsabteilung (IE, Lean etc.)", "Weitere"],
    index=None,
    key="funktion_radio_input"
    )
    
    st.subheader("Spezifische technische und prozessuale Angaben")

   # CNC-Maschinen
    cnc_options = ["< 5", "5-10", "11-24", "≥ 25"]
    selected_cnc_range = st.radio(
        "Wie viele CNC-Werkzeugmaschinen haben Sie in Ihrer zerspanenden Fertigung?",
        cnc_options,
        key="cnc_range"
    )
    st.session_state.anzahl_cnc_werkzeugmaschinen_categorized = categorize_cnc_machines(selected_cnc_range)

    # Automatisierungsgrad
    automation_percentage_options = ["0%", "1-25%", "26-49%", "≥ 50%"]
    selected_automation_range = st.radio(
        "Wie viel Prozent Ihrer CNC-Werkzeugmaschinen besitzen eine Automation für den Werkstückwechsel?",
        automation_percentage_options,
        key="automation_range"
    )
    st.session_state.automatisierungsgrad_categorized = categorize_automation_percentage(selected_automation_range)

    # Losgröße
    losgroesse_options = ["< 5", "5-50", "51-99", "≥ 100"]
    selected_losgroesse = st.radio(
        "Welche durchschnittlichen Losgrößen werden bei Ihnen gefertigt?",
        losgroesse_options,
        key="losgroesse_range"
    )
    st.session_state.losgroesse_categorized = categorize_losgroesse(selected_losgroesse)

    # Durchlaufzeit
    durchlaufzeit_options = ["< 10 min", "11-30 min", "31-89 min", "≥ 90 min"]
    selected_durchlaufzeit = st.radio(
        "Wie lang ist die durchschnittliche Durchlaufzeit (von Rohmaterial bis zum unentgrateten Fertigteil) eines Auftrags über alle Maschinen?",
        durchlaufzeit_options,
        key="durchlaufzeit_range"
    )
    st.session_state.durchlaufzeit_categorized = categorize_durchlaufzeit(selected_durchlaufzeit)

    # Laufzeit
    laufzeit_options = ["< 1 Tag", "1-3 Tage", "4-6 Tage", "≥ 7 Tage"]
    selected_laufzeit = st.radio(
        "Welche durchschnittliche Laufzeit haben die Werkstücke, welche bei Ihnen gefertigt werden?",
        laufzeit_options,
        key="laufzeit_range"
    )
    st.session_state.laufzeit_categorized = categorize_laufzeit(selected_laufzeit)
   
    st.text_input("PLZ (optional)", key="plz_input") # Eindeutiger Key
    st.text_input("E-Mail (optional)", key="email_input") # Eindeutiger Key
    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")

elif current_tab == "Auswertung":
    if st.session_state.get('ergebnisse') and st.session_state.ergebnisse:
        
        # Labels & Werte sammeln
        labels, values = [], []
        for dim_name, handlungsfelder_in_dim in mtok_structure.items():
            for hf_name in handlungsfelder_in_dim:
                val = st.session_state.ergebnisse.get(hf_name)
                if val is not None:
                    labels.append(f"{hf_name} ({dim_name})")
                    values.append(val)

        # Radar-Chart erzeugen, falls Werte vorhanden
        if values and all(isinstance(v, (int, float)) for v in values):
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            values_cycle = values + values[:1]
            angles_cycle = angles + angles[:1]
            wrapped_labels = [label.replace(" und ", "\nund ").replace("(", "\n(") for label in labels]

            radar_chart_fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
            ax.fill(angles_cycle, values_cycle, color='cornflowerblue', alpha=0.3)
            ax.plot(angles_cycle, values_cycle, color='royalblue', linewidth=1)
            ax.set_yticks([1, 2, 3, 4])
            ax.set_yticklabels(['1', '2', '3', '4'], fontsize=6)
            ax.set_xticks(angles)
            ax.set_xticklabels(wrapped_labels, fontsize=5)
            ax.set_title("Readiness-Profil", fontsize=12, pad=10)
            plt.tight_layout()

            # Versuche zuerst als PNG über BytesIO (schärfer)
            try:
                buf_streamlit = BytesIO()
                radar_chart_fig.savefig(buf_streamlit, format="png", dpi=200, bbox_inches="tight")
                buf_streamlit.seek(0)

                if buf_streamlit.getbuffer().nbytes > 0:
                    st.image(buf_streamlit, caption="Readiness-Profil", width=700)
                else:
                    st.warning("🛑 Bild-Buffer ist leer – zeige Fallback-Chart mit st.pyplot()")
                    st.pyplot(radar_chart_fig)
        
            except Exception as e:
                st.error(f"Fehler beim Anzeigen des Diagramms: {e}")
                st.pyplot(radar_chart_fig)
        else:
            st.warning("❗ Keine gültigen Werte für Radar-Diagramm vorhanden.")

         # Cluster-Zuordnung
        cluster_result, abweichungen_detail = berechne_clusterzuordnung(Kriterien)
        display_cluster_result = cluster_result

        if isinstance(cluster_result, str) and "Bitte bewerten Sie" in cluster_result:
            st.warning(cluster_result)
        else:
            st.subheader("Automatische Clusterzuordnung")
            st.success(f"Der Betrieb wird dem folgenden Cluster zugeordnet:\n\n**{cluster_result}**")

            # GPT-Auswertung
            st.subheader("Individuelle, KI-gestützte Handlungsempfehlung")
            with st.spinner("Die Handlungsempfehlungen werden generiert..."):
                gpt_output_text = frage_chatgpt_auswertung(st.session_state.ergebnisse, cluster_result)

            def markdown_to_html(text):
                text = re.sub(r"^### (.*)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
                text = re.sub(r"^#### (.*)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
                text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
                text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
                text = re.sub(r"^- (.*?)$", r"<li>\1</li>", text, flags=re.MULTILINE)
                text = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", text, flags=re.DOTALL)
                return text

            gpt_text_html_ready = markdown_to_html(gpt_output_text)
            st.markdown(gpt_text_html_ready, unsafe_allow_html=True)

        # Radar-Grafik für HTML
        if radar_chart_fig:
            buf = BytesIO()
            radar_chart_fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            img_tag = f'<img src="data:image/png;base64,{img_base64}" style="width: 600px; height: auto; margin-top: 20px;">'
        else:
            img_tag = ""

        # Tabelle
        table_rows = ""
        for dim_name, handlungsfelder_in_dim in mtok_structure.items():
            for hf_name in handlungsfelder_in_dim:
                val = st.session_state.ergebnisse.get(hf_name)
                if val is not None:
                    table_rows += f"<tr><td>{hf_name}</td><td>{dim_name}</td><td style='text-align: center;'>{val:.1f}</td></tr>"

        table_html = f"""
        <h2>Bewertung der Handlungsfelder</h2>
        <table>
            <thead><tr><th>Handlungsfeld</th><th>MTOK-Dimension</th><th>Mittelwert</th></tr></thead>
            <tbody>{table_rows}</tbody>
        </table>
        """
        
        # Fallback, falls GPT-Text nicht generiert wurde
        if "gpt_text_html_ready" not in locals():
            gpt_text_html_ready = "<p>Keine Empfehlung generiert.</p>"
        
        # HTML-Komplettausgabe
        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="utf-8">
            <title>Readiness-Auswertung</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: auto; line-height: 1.6; }}
                h1 {{ font-size: 26px; color: #003366; }}
                h2 {{ font-size: 20px; color: #005599; margin-top: 30px; }}
                .box {{ background: #f8f9fa; padding: 15px; border-left: 5px solid #005599; border-radius: 5px; margin-bottom: 25px; }}
                .gpt-box {{ background-color: #eef7ff; border-left: 5px solid #0099cc; }}
                img {{ display: block; margin: 20px auto; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; font-size: 13px; }}
                th {{ background-color: #e1e9f0; text-align: left; }}
                td:nth-child(3) {{ text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Ergebnisse des Readiness-Checks</h1>
            <div class="box"><strong>Clusterzuordnung:</strong><br>{display_cluster_result}</div>
            <h2>Individuelle Handlungsempfehlungen</h2>
            <div class="box gpt-box">{gpt_text_html_ready}</div>
            <h2>Readiness-Profil</h2>{img_tag}
            {table_html}
        </body>
        </html>
        """

        st.download_button(
            label="📄 Ergebnisse als HTML herunterladen",
            data=html_content,
            file_name="auswertung.html",
            mime="text/html"
        )
        
# Trenner
st.markdown("---")

# Navigationsbuttons unten
nav_buttons("bottom")

# Fester Nach-oben-Button
st.markdown(
    """
    <a href="#top">
        <div style='position: fixed; bottom: 40px; left: 50%; transform: translateX(-50%);
                    z-index: 9999;'>
            <button style='background-color: #1f77b4; color: white; border: none;
                            padding: 10px 16px; border-radius: 6px; font-size: 16px;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.2); cursor: pointer;'>
                ⬆ Nach oben
            </button>
        </div>
    </a>
    """,
    unsafe_allow_html=True
)
