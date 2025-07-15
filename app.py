import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai # type: ignore
import io # Für das Speichern von Bildern/PDFs im Speicher
from fpdf import FPDF # Für die PDF-Generierung

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
      "begründung": "Kenntnisse über IT-Zugänge, Prozessintegration und Selbstorganisation sind essenziell. Unklarheiten führen zu Produktivitätsverlusten."
    },
    {
      "frage": "M1.2 Beschäftigte kennen die Anforderungen an zeitflexible Arbeit in der Fertigung.",
      "begründung": "Zeitliche Flexibilität muss mit technischen Abläufen abgestimmt sein. Nur so ist eine realistische Umsetzung in der Zerspanung möglich."
    },
    {
      "frage": "M1.3 Beschäftigte verfügen über fachliche und digitale Kompetenzen zur Selbststeuerung.",
      "begründung": "Produktive flexible Arbeit erfordert eigenständige Prozesskontrolle und Informationsverarbeitung."
    },
    {
      "frage": "M1.4 Beschäftigte übernehmen Aufgaben, die ortsunabhängig erledigt werden können.",
      "begründung": "Ein breites Aufgabengebiet (z. B. Programmierung von CNC-Werkzeugmaschinen, Fertigungsdokumentationen) fördert Eigenverantwortung und unterstützt mobile Arbeitsformen."
    },
    {
      "frage": "M1.5 Beschäftigte können Störungen eigenständig lösen.",
      "begründung": "Flexibles Arbeiten erfordert Handlungssicherheit bei Prozessabweichungen ohne direkte Unterstützung."
    },
    {
      "frage": "M1.6 Die Arbeitsumgebung ermöglicht produktives Arbeiten außerhalb der Fertigung.",
      "begründung": "Ergonomische, digitale und akustische Bedingungen sichern Leistung zwischen Beschäftigten auch bei räumlicher Entkopplung."
    },
    {
      "frage": "M1.7 Beschäftigte erhalten gezielte Qualifizierungen zu mobilen und zeitflexiblen Arbeitsformen.",
      "begründung": "Kompetenzaufbau fördert Motivation und langfristige Bindung an flexible Arbeitsmodelle."
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
      "frage": "M2.5 Beschäftigte beherrschen digitale Standardtools.",
      "begründung": "Digitale Anwendungskompetenz ist grundlegend für effektive Kollaboration (z. B. ERP-Software, Mailprogramm, Programmierungsoftware)."
    },
    {
      "frage": "M2.6 Beschäftigte verfügen über stabile externe Bedingungen für mobiles Arbeiten.",
      "begründung": "Rückzugsorte und unterstützendes Umfeld sind entscheidend für die Umsetzbarkeit."
    },
    {
      "frage": "M2.7 Beschäftigte können aktiv Verbesserungsvorschläge einbringen.",
      "begründung": "Beteiligung fördert die Passung und Akzeptanz flexibler Konzepte (z. B. KVP-Prozess)."
    },
    {
      "frage": "M2.8 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren Grundfunktionen.",
      "begründung": "Systemverständnis erhöht Handlungssicherheit und reduziert Fehlbedienungen."
    }
  ],
   "Arbeitsplatzgestaltung und Automatisierung": [
    {
    "frage": "T1.1 CNC-Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
    "begründung": "Ein hoher Automatisierungsgrad oder lange unbeaufsichtigte Laufzeiten ermöglichen zeitliche Entkopplung und reduzieren Präsenzzwänge."
    },
    {
    "frage": "T1.2 Präsenzgebundene Aufgaben (z. B. Maschineneinrichtung) können gebündelt und zeitlich verdichtet ausgeführt werden.",
    "begründung": "Planbare Präsenzphasen reduzieren Unterbrechungen und erleichtern mobile Arbeitsanteile außerhalb dieser Kernzeiten."
    },
    {
    "frage": "T1.3 Tätigkeiten an Maschinenarbeitsplätzen sind flexibel zwischen Beschäftigten übertragbar.",
    "begründung": "Aufgabenübertragbarkeit schafft Spielräume bei Personalengpässen, fördert Vertretungsfähigkeit und ermöglicht die Mehrmaschinenbedienung."
    },
    {
    "frage": "T1.4 Maschinenbedienung erfolgt auf Basis standardisierter und dokumentierter Abläufe.",
    "begründung": "Standardisierung ermöglicht Übergaben, unterstützt mobile Anteile und erleichtert Schulung sowie Fernbedienung."
    },
    {
    "frage": "T1.5 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm.",
    "begründung": "Prozessstabilität ist Voraussetzung für entkoppelte Arbeitsformen und reduziert unvorhergesehene Eingriffe bei physischer Abwesenheit."
    },
    {
    "frage": "T1.6 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert.",
    "begründung": "Sensorische oder visuelle Fernkontrolle (z. B. Kameras, Monitoring-Apps, Maschinenzugriff) reduziert Präsenznotwendigkeit und erlaubt situatives Eingreifen."
    },
    {
    "frage": "T1.7 Prüf- und Qualitätssicherungsprozesse sind automatisiert oder organisatorisch entkoppelt.",
    "begründung": "Entkoppelte Qualitätssicherung reduziert feste Rückmeldepunkte im Prozess und ermöglicht flexiblere Zeiteinteilung."
    },
    {
    "frage": "T1.8 Wartungsbedarfe und Eingriffsprotokolle sind digital dokumentiert und zentral zugänglich.",
    "begründung": "Digitale Transparenz unterstützt Eigenverantwortung, Übergaben und hybride Zuständigkeiten."
    },
    {
    "frage": "T1.9 Echtzeitdaten zur Maschinenauslastung sind digital verfügbar.",
    "begründung": "Prozessdaten (z. B. OEE-Analyse, Laufzeitanalyse) ermöglichen auch bei variabler Anwesenheit situationsabhängige Steuerung und Optimierung."
    },
    {
    "frage": "T1.10 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
    "begründung": "Vernetzte Systeme (z. B. ERP, MES, BDE) sind Voraussetzung für ortsunabhängige Steuerung, Planung und Dokumentation."
    },
    {
    "frage": "T1.11 Die Auswirkungen flexibler Arbeit auf Produktivität, Qualität und Maschinenauslastung werden regelmäßig erfasst.",
    "begründung": "Systematische Erfolgskontrolle unterstützt kontinuierliche Verbesserung und Legitimation flexibler Arbeitsmodelle im Produktionsbereich."
    }
   ],
   "IT-Systemlandschaft und digital vernetzte Infrastruktur": [
    {
      "frage": "T2.1 Die IT-Infrastruktur stellt geeignete mobile Endgeräte zur Verfügung.",
      "begründung": "Mobile Endgeräte (z. B. Laptops, Tablets) bilden die technische Basis für ortsunabhängiges Arbeiten in produktionsnahen Tätigkeiten."
    },
    {
      "frage": "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich.",
      "begründung": "Flexibles Arbeiten erfordert sicheren Zugang (z. B. über VPN-Verbindungen) zu zentralen Anwendungen von außerhalb der Fertigung."
    },
    {
      "frage": "T2.3 Digitale Kommunikations- und Kollaborationstools sind standardisiert verfügbar.",
      "begründung": "Digitale Tools (z. B. MS Teams, Slack) ermöglichen dezentrale Abstimmung, Informationsaustausch und Teamkommunikation."
    },
    {
      "frage": "T2.4 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar.",
      "begründung": "Zuverlässiger IT-Support sichert technische Funktionsfähigkeit und reduziert Akzeptanzbarrieren."
    },
    {
      "frage": "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
      "begründung": "Vernetzung fördert bereichsübergreifende Koordination und reduziert Medienbrüche in Echtzeitprozessen."
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
      "frage": "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
      "begründung": "Ein effektiver und transparenter Informationsfluss ist die Grundlage für dezentrale Koordination, schnelle Reaktionsfähigkeit und den Ausgleich personeller Ausfälle."
    },
    {
      "frage": "O1.2 Digitale Kommunikations- und Kollaborationstools (inkl. asynchrone Formate und hybride Besprechungen) sind standardisiert verfügbar, technisch unterstützt und sicher nutzbar.",
      "begründung": "Standardisierte digitale Tools ermöglichen orts- und zeitunabhängige Abstimmung, Teamkommunikation und flexible Teilhabe an Besprechungen."
    },
    {
      "frage": "O1.3 Die digitale Kommunikationskompetenz der Beschäftigten wird systematisch gefördert und neue strukturiert in den digitale Kooperationsprozesse eingeführt.",
      "begründung": "Mediensouveränität und eine fundierte Einarbeitung sind Voraussetzungen für eine funktionierende digitale Zusammenarbeit und Akzeptanz in verteilten Teams."
    },
    {
      "frage": "O1.4 Die Organisation reflektiert und passt ihre Kommunikationsstrukturen regelmäßig an, um Zielerreichung und Zusammenarbeit kontinuierlich zu optimieren.",
      "begründung": "Eine lernende Organisation passt ihre Kommunikationsprozesse an neue Arbeitsformen an, um Passung zu stärken und Konflikte bei zeitlicher Flexibilität zu vermeiden."
    },
    {
      "frage": "O1.5 Erfahrungswissen wird systematisch dokumentiert, digital zugänglich gemacht und aktiv weitergegeben.",
      "begründung": "Strukturierter Wissenstransfer (z.B. Best Practices, Lernmaterialien) sichert Qualität, fördert kontinuierliches Lernen und reduziert Abhängigkeiten von einzelnen Personen bei flexiblen Arbeitsmodellen."
    },
    {
      "frage": "O1.6 Es existieren umfassende Datenschutzrichtlinien und klare Regeln für den Umgang mit allen Daten, insbesondere personenbezogenen.",
      "begründung": "Transparente und verbindliche Datenschutzregelungen schaffen Vertrauen, sichern Rechtssicherheit und verhindern missbräuchliche Datennutzung im Kontext mobiler Arbeit."
    },
    {
      "frage": "O1.7 IT-Sicherheitskonzepte sind etabliert, werden regelmäßig geprüft und gewährleisten den Schutz vor externen Angriffen und Datenverlust.",
      "begründung": "Robuste IT-Sicherheitsmaßnahmen (z. B. VPN-Verbindungen) sind fundamental für den Schutz sensibler Produktions- und Unternehmensdaten und zur Aufrechterhaltung der Betriebskontinuität bei flexibler Arbeit."
    },
    {
      "frage": "O1.8 Verantwortlichkeiten für IT-Sicherheit und Datenschutz sind eindeutig definiert, und relevante Stakeholder (z.B. Betriebsrat, Datenschutzbeauftragte) sind aktiv in die Gestaltung eingebunden.",
      "begründung": "Klare Rollen und eine partizipative Einbindung relevanter Akteure fördern die Akzeptanz, gewährleisten die Einhaltung rechtlicher Rahmenbedingungen und stärken die Governance-Struktur."
    }
    ],
    "Soziokulturelle und organisatorische Umwelt": [
    {
      "frage": "O2.1 Der Betrieb verfügt über ausreichend qualifizierte Fachkräfte in der zerspanenden Fertigung.",
      "begründung": "Fachkräftesicherung ist die Grundlage produktiver Flexibilisierung. Ohne entsprechende Qualifikation scheitern mobile und zeitflexible Modelle bereits in der Umsetzung."
    },
    {
      "frage": "O2.2 Die Personalplanung berücksichtigt den flexiblen Einsatz über unterschiedliche Zeiten und Orte hinweg.",
      "begründung": "Eine vorausschauende Planung schafft Handlungsspielräume für mobile und zeitflexible Einsätze, insbesondere im Schichtsystem oder bei wechselnden Anforderungen."
    },
    {
      "frage": "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und zeitflexibler Arbeit.",
      "begründung": "Klare Regelungen schaffen Rechtssicherheit und Orientierung."
    },
    {
      "frage": "O2.4 Externe Anforderungen von Kunden, Lieferanten oder Partnern werden in der Flexibilitätsstrategie berücksichtigt.",
      "begründung": "Schnittstellen zu externen Akteuren müssen abgestimmt sein, damit flexible Arbeitsformen betrieblich und marktseitig umsetzbar sind."
    },
    {
      "frage": "O2.5 Rechtliche Rahmenbedingungen sind bekannt und werden beachtet.",
      "begründung": "Rechtskonformität (z. B. Arbeitszeitgesetz, Datenschutz) erhöht die Akzeptanz flexibler Arbeit und verhindert Unsicherheiten oder Fehlentwicklungen."
    },
    {
      "frage": "O2.6 Arbeitszeitmodelle sind in Planungs- und Steuerungssysteme integriert.",
      "begründung": "Nur durch die Integration in digitale Systeme (z. B. MES, ERP) können flexible Modelle zuverlässig geplant, dokumentiert und gesteuert werden."
    },
    {
      "frage": "O2.7 Die Aufbau- und Ablauforganisation ist anpassungsfähig.",
      "begründung": "Strukturelle Anpassungsfähigkeit (z. B. bei Sonderaufträgen oder kurzfristigen Vertretungen) ist Voraussetzung für spontane Reaktion und produktive Umsetzung von Flexibilität."
    },
    {
      "frage": "O2.8 Die Verantwortung der Führungskräfte für die Umsetzung flexibler Arbeit ist eindeutig definiert.",
      "begründung": "Unklare Rollen behindern Fortschritt. Führungskräfte sind entscheidend für die Gestaltung, Steuerung und Akzeptanz flexibler Arbeitsformen."
    },
    {
      "frage": "O2.9 Zuständigkeiten und Vertretungsregelungen sind auch bei mobiler Arbeit klar definiert.",
      "begründung": "Eindeutige Verantwortlichkeiten sichern die Prozessstabilität bei mobiler Arbeit und entlasten das Team."
    },
    {
      "frage": "O2.10 Rückmeldungen zur Umsetzung flexibler Arbeit werden regelmäßig eingeholt und genutzt.",
      "begründung": "Systematisches Feedback stärkt die Passung und ermöglicht lernorientierte Anpassungen der Flexibilisierungsstrategie."
    },
    {
      "frage": "O2.11 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten.",
      "begründung": "Die Möglichkeit zur Mitgestaltung ist empirisch als signifikanter Einflussfaktor für erfolgreiche Flexibilisierung belegt."
    },
    {
      "frage": "O2.12 Pausen können im Rahmen betrieblicher Vorgaben flexibel genommen werden.",
      "begründung": "Zeitliche Autonomie bei Pausen erhöht Erholungseffekte, unterstützt eigenverantwortliche Taktung und stärkt die Selbstbestimmung im Arbeitsprozess."
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
    "frage": "O3.6 Personelle Puffer zur Kompensation von Engpässen sind eingeplant.",
      "begründung": "Ausweichkapazitäten sind essenziell, um individuelle Flexibilität ohne Produktivitätsverlust zu ermöglichen."
    },
    {
      "frage": "O3.7 Rüstprozesse sind kurz, standardisiert und in die Planung integriert.",
      "begründung": "Effiziente Rüstprozesse erhöhen die Steuerbarkeit und Reaktionsgeschwindigkeit bei flexiblen Arbeitszeiten."
    },
    {
      "frage": "O3.8 Operative Führungskräfte können dezentral Anpassungen in der Steuerung vornehmen.",
      "begründung": "Dezentrale Entscheidungskompetenz erhöht Reaktionsfähigkeit bei sich ändernden Anwesenheiten und Aufgabenverteilungen."
    },
    {
      "frage": "O3.9 Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten.",
      "begründung": "Toleranz gegenüber kurzfristiger Abwesenheit eröffnet Möglichkeiten für zeitautonome Arbeitsgestaltung."
    },
    {
      "frage": "O3.10 Qualitätskontrollen sind prozessintegriert oder digital unterstützt.",
      "begründung": "Die Integration in den Prozessverlauf oder digitale Unterstützung ermöglichen entkoppelte Kontrollmechanismen."
    },
    {
      "frage": "O3.11 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
      "begründung": "Digitale Vernetzung und Flexibilität der Steuerung ermöglichen schnelle Reaktionen auf sich ändernde Rahmenbedingungen."
    },
    {
      "frage": "O3.12 Produktionsprozesse sind standardisiert dokumentiert und übertragbar.",
      "begründung": "Standardisierung erleichtert Vertretungen, Übergaben und mobile Unterstützungsformate."
    }
    ],
    "Unternehmenskultur": [
    {
    "frage": "K1.1 Im Unternehmen wird Vertrauen als Grundlage der Zusammenarbeit gelebt.",
      "begründung": "Vertrauen ist elementar für mobile und zeitflexible Arbeit, da Kontrolle nicht über physische Präsenz erfolgen kann."
    },
    {
    "frage": "K1.2 Beschäftigte erhalten Handlungsfreiräume zur Gestaltung ihrer Arbeit.",
      "begründung": "Handlungsspielräume fördern Motivation, Eigenverantwortung und Innovationspotenzial – zentrale Voraussetzungen für flexible Arbeit."
    },
    {
    "frage": "K1.3 Zielerreichung hat Vorrang vor physischer Anwesenheit.",
      "begründung": "Ergebnisorientierung statt Präsenzkultur stärkt Flexibilisierung und Leistungsfokus."
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
      "frage": "K1.6 Flexible Arbeit ist als selbstverständlicher Bestandteil der betrieblichen Praxis etabliert.",
      "begründung": "Normalisierung von Flexibilität reduziert Widerstände und erhöht die organisatorische Anschlussfähigkeit."
    },
    {
      "frage": "K1.7 Es bestehen keine verdeckten Erwartungen an ständige Erreichbarkeit.",
      "begründung": "Kulturelle Entgrenzung gefährdet Erholung, Selbststeuerung und nachhaltige Nutzung flexibler Arbeitsformen."
    },
    {
      "frage": "K1.8 Unterschiedliche Arbeitsstile und -rhythmen werden anerkannt und integriert.",
      "begründung": "Individuelle Unterschiede fördern Anpassungsfähigkeit und stärken das kulturelle Verständnis für Diversität."
    },
    {
      "frage": "K1.9 Mobile Arbeit wird systematisch in Teamabstimmungen integriert.",
      "begründung": "Kulturelle Integration erfordert explizite Berücksichtigung dezentraler Arbeit in Kommunikationsprozesse."
    },
    {
      "frage": "K1.10 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
      "begründung": "Transparente Diskussion über Zielkonflikte stärkt Vertrauen und vermeidet dysfunktionale Idealisierungen."
    },
    {
      "frage": "K1.11 Kulturelle Barrieren bei der Einführung flexibler Arbeit werden systematisch erfasst und reflektiert.",
      "begründung": "Nur durch strukturiertes Feedback lassen sich kulturelle Hürden identifizieren und gezielt adressieren."
    }
    ],
   "Soziale Beziehungen und Interaktion": [
    {
      "frage": "K2.1 Die Unternehmensführung positioniert sich aktiv und lebt Flexibilität sichtbar vor.",
      "begründung": "Ein strategisch sichtbares Commitment erhöht die Legitimität flexibler Arbeit und schafft Orientierung für nachgelagerte Führungsebenen."
    },
    {
      "frage": "K2.2 Die direkte Führungskraft unterstützt aktiv mobile und zeitflexible Arbeitsformen.",
      "begründung": "Unmittelbare Vorgesetzte sind entscheidend für die praktische Umsetzung flexibler Arbeit im Alltag."
    },
    {
      "frage": "K2.3 Führungskräfte fördern gezielt Eigenverantwortung und Selbstorganisation im Team.",
      "begründung": "Selbststeuerung ist eine zentrale Voraussetzung flexibler Arbeit und muss durch Führung aktiv gestärkt werden."
    },
    {
      "frage": "K2.4 Führung erfolgt ergebnisorientiert statt anwesenheitsorientiert.",
      "begründung": "Flexibles Arbeiten erfordert eine Bewertung auf Grundlage von Zielerreichung, nicht physischer Präsenz."
    },
    {
      "frage": "K2.5 Führungskräfte verfügen über Kompetenzen zur Steuerung hybrider Teams.",
      "begründung": "Hybride Arbeit stellt neue Anforderungen an Führung, insbesondere im Umgang mit virtueller Kommunikation und dezentraler Koordination."
    },
    {
      "frage": "K2.6 Es existieren verbindliche Kommunikationsstandards im Team.",
      "begründung": "Verlässliche Kommunikationsprozesse (z. B. Regeltermine, Reaktionszeiten) kompensieren informelle Interaktionen bei physischer Distanz."
    },
    {
      "frage": "K2.7 Die Teamkultur ist durch gegenseitige Unterstützung und Kooperation geprägt.",
      "begründung": "Soziale Unterstützung erhöht Resilienz – ein zentraler Erfolgsfaktor bei reduzierter Präsenz."
    },
    {
      "frage": "K2.8 Es bestehen etablierte Formate für den informellen Austausch im Team.",
      "begründung": "Informelle Kommunikation fördert Vertrauen und Zusammenhalt – auch bei räumlicher Trennung."
    },
    {
      "frage": "K2.9 Teamziele und die Qualität der Zusammenarbeit werden regelmäßig reflektiert und angepasst.",
      "begründung": "Gemeinsame Reflexion stärkt Selbststeuerung und fördert kontinuierliche Weiterentwicklung."
    },
    {
      "frage": "K2.10 Teammitglieder kennen ihre Rollen und Verantwortlichkeiten im flexiblen Arbeitskontext.",
      "begründung": "Klare Rollenklarheit erhöht Handlungssicherheit und reduziert Koordinationsaufwand."
    },
    {
      "frage": "K2.11 Konflikte im Team werden frühzeitig erkannt und konstruktiv moderiert.",
      "begründung": "Konstruktiver Umgang mit Konflikten ist in asynchronen oder hybriden Teams besonders relevant."
    },
    {
      "frage": "K2.12 Unterschiedliche Bedürfnisse werden teamintern berücksichtigt.",
      "begründung": "Eine faire Berücksichtigung individueller Anforderungen (z. B. Schichtsystem, Pflegeverantwortung) fördert Akzeptanz und Zusammenhalt im Team."
    }
  ]
    }

# --- Hilfsfunktionen ---
def categorize_cnc_machines(num_machines_raw):
    if num_machines_raw is None:
        return np.nan
    mapping = {
        "< 5": 1,
        "5 - 10": 2,
        "11 - 24": 3,
        "≥ 25": 4
    }
    return mapping.get(num_machines_raw, np.nan)
    
def categorize_automation_percentage(percentage_str):
    if percentage_str is None:
        return np.nan
    mapping = {
        "0%": 1,
        "1 - 25%": 2,
        "26 - 49%": 3,
        "≥ 50%": 4
    }
    return mapping.get(percentage_str, np.nan)

def categorize_losgroesse(losgroesse_str):
    mapping = {
        "<5": 1,
        "5–50": 2,
        "51–99": 3,
        "≥ 100": 4
    }
    return mapping.get(losgroesse_str, np.nan)

def categorize_durchlaufzeit(durchlaufzeit_str):
    mapping = {
        "<10 min": 1,
        "11–30 min": 2,
        "31–89 min": 3,
        "≥ 90 min": 4
    }
    return mapping.get(durchlaufzeit_str, np.nan)

def categorize_laufzeit(laufzeit_str):
    mapping = {
        "<1 Tag": 1,
        "1–3 Tage": 2,
        "4–6 Tage": 3,
        "≥ 7 Tage": 4
    }
    return mapping.get(laufzeit_str, np.nan)


# Mapping von Kriterien-Item-Fragen zu den 11 Cluster-Variablen
# WICHTIG: Die Liste der Fragen muss exakt der 'frage'-Eigenschaft in den Kriterien-Dictionaries entsprechen.
# Falls eine Variable nur durch ein einziges Item repräsentiert wird, ist die Liste trotzdem notwendig.
# Falls eine Variable durch mehrere Items repräsentiert wird, wird ihr Wert als Mittelwert dieser Items berechnet.
kriterien_item_to_cluster_variable_mapping = {
    # Cluster Variable : [Liste von Fragen-Strings aus dem Kriterien-Dictionary]
    
    # 1. Automatisierungsgrad (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 2. Anzahl CNC-Werkzeugmaschinen (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 3. Losgröße (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 4. Durchlaufzeit (Wert kommt direkt aus der "Abschließende Fragen" Sektion)
    # 5. Laufzeit (Wert kommt direkt aus der "Abschließende Fragen" Sektion)

    # Diese 5 Variablen werden direkt abgefragt und müssen hier NICHT gemappt werden.
    # Ihre Werte werden in berechne_clusterzuordnung separat verarbeitet.

    # 6. Digitalisierungsgrad
    "Digitalisierungsgrad": [
        "T1.10 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
        "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
        "M2.8 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren Grundfunktionen.",
        "T2.6 Die IT-Systeme ermöglichen ortsunabhängige Einsicht und Rückmeldungen in produktionsrelevante Echtzeitdaten.",
        "T2.7 Simulationen oder digitale Zwillinge werden zur Produktionsplanung und -steuerung eingesetzt.",
        "O2.6 Arbeitszeitmodelle sind in Planungs- und Steuerungssysteme integriert.",
        "O3.11 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar."
    ],
    
    # 7. Prozessinstabilität
    "Prozessinstabilität": [
        "T1.5 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm", # Niedriger Wert hier bedeutet hohe Instabilität (daher Skala invertiert für dieses Item bei Berechnung)
        "O3.9 Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten." # Toleranz gegenüber Stillständen reduziert Instabilität
    ],
    
    # 8. Nutzen (Wahrgenommener Nutzen von Flexibilität)
    "Nutzen": [
        "T1.11 Die Auswirkungen flexibler Arbeit auf Produktivität, Qualität und Maschinenauslastung werden regelmäßig erfasst.",
        "K1.3 Zielerreichung hat Vorrang vor physischer Anwesenheit.",
        "K1.6 Flexible Arbeit ist als selbstverständlicher Bestandteil der betrieblichen Praxis etabliert.", # Impliziert wahrgenommenen Nutzen
        "K2.4 Führung erfolgt ergebnisorientiert statt anwesenheitsorientiert."
    ],
    
    # 9. Akzeptanz
    "Akzeptanz": [
        "M2.1 Beschäftigte stehen mobiler Arbeit aufgeschlossen gegenüber.",
        "M2.2 Beschäftigte stehen zeitflexibler Arbeit offen gegenüber.",
        "K1.4 Es herrscht ein positives Verständnis für neue Arbeitsformen.",
        "K1.6 Flexible Arbeit ist als selbstverständlicher Bestandteil der betrieblichen Praxis etabliert.",
        "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und zeitflexibler Arbeit.",
        "O2.10 Rückmeldungen zur Umsetzung flexibler Arbeit werden regelmäßig eingeholt und genutzt."
    ],
    
    # 10. Aufwand Zeit (Wahrgenommener Zeitaufwand für flexible Arbeit)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Score der zugewiesenen Fragen INVERTIERT,
    # da ein HOHEr Score in der Frage ("können mitgestalten") einen NIEDRIGEN "Aufwand Zeit" für das Cluster bedeutet.
    "Aufwand Zeit": [
        "O2.11 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten.",
        "O1.2 Digitale Kommunikations- und Kollaborationstools (inkl. asynchrone Formate und hybride Besprechungen) sind standardisiert verfügbar, technisch unterstützt und sicher nutzbar.",
        "O1.4 Die Organisation reflektiert und passt ihre Kommunikationsstrukturen regelmäßig an, um Zielerreichung und Zusammenarbeit kontinuierlich zu optimieren."
    ],
    
    # 11. Aufwand Mobil (Wahrgenommener Aufwand für mobiles Arbeiten)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Score der zugewiesenen Fragen INVERTIERT,
    # da ein HOHEr Score in der Frage ("Arbeitsumgebung ermöglicht") einen NIEDRIGEN "Aufwand Mobil" für das Cluster bedeutet.
    "Aufwand Mobil": [
        "M1.6 Die Arbeitsumgebung ermöglicht produktives Arbeiten außerhalb der Fertigung.",
        "M2.6 Beschäftigte verfügen über stabile externe Bedingungen für mobiles Arbeiten.",
        "T2.4 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar.",
        "O1.8 Verantwortlichkeiten für IT-Sicherheit und Datenschutz sind eindeutig definiert, und relevante Stakeholder (z.B. Betriebsrat, Datenschutzbeauftragte) sind aktiv in die Gestaltung eingebunden.",
        "T1.6 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert."
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


# Clusterermittlung (angepasst, um die 11 spezifischen Cluster-Variablen zu berechnen und dann zu vergleichen)
def berechne_clusterzuordnung(kriterien_all_items_dict):
    # 1. Sammle alle individuellen Item-Bewertungen aus der Streamlit Session State
    all_item_scores_flat = {}
    for dim_name, handlungsfelder_in_dim in mtok_structure.items():
        for hf_name in handlungsfelder_in_dim:
            if hf_name in kriterien_all_items_dict:
                for idx, item_info in enumerate(kriterien_all_items_dict[hf_name]):
                    item_key_in_session = f"{dim_name}_{hf_name}_{idx}"
                    if item_key_in_session in st.session_state and st.session_state[item_key_in_session] is not None:
                        all_item_scores_flat[item_info['frage']] = st.session_state[item_key_in_session]

    # 2. Berechne die Werte für die 11 spezifischen Cluster-Variablen des Nutzers
    nutzer_cluster_variable_werte = {}

    # Sonderbehandlung für die 5 direkt abgefragten Cluster-Variablen
    # Diese werden direkt aus st.session_state geholt, da sie separat kategorisiert wurden.
    direct_input_vars = [
        "Anzahl CNC-Werkzeugmaschinen", 
        "Automatisierungsgrad", 
        "Losgröße", 
        "Durchlaufzeit", 
        "Laufzeit"
    ]
    for var_name in direct_input_vars:
        session_key_categorized = var_name.lower().replace(" ", "_") + "_categorized" # Erzeugt z.B. "losgröße_categorized"
        if session_key_categorized in st.session_state:
            value = st.session_state[session_key_categorized]
            if isinstance(value, (int, float)) and not np.isnan(value):
                nutzer_cluster_variable_werte[var_name] = value
            else:
                nutzer_cluster_variable_werte[var_name] = float('nan')
        else:
            nutzer_cluster_variable_werte[var_name] = float('nan')

    # Behandlung der restlichen Variablen, die aus Kriterien-Items gemappt werden
    # Nur noch die Variablen, die NICHT direkt abgefragt werden, müssen hier behandelt werden.
    for cluster_var_name, associated_item_questions in kriterien_item_to_cluster_variable_mapping.items():
        # Diese Variablen wurden oben nicht direkt als input_vars behandelt
        if cluster_var_name not in direct_input_vars: 
            scores_for_variable = []
            for q_text in associated_item_questions:
                if q_text in all_item_scores_flat:
                    scores_for_variable.append(all_item_scores_flat[q_text])
            
            if scores_for_variable:
                calculated_score = np.mean(scores_for_variable)
                
                # Skalen-Invertierung für "Aufwand" und "Prozessinstabilität" (höherer Score in Frage bedeutet besser/weniger Problem)
                # Im Clusterprofil bedeuten hohe Werte für diese Variablen einen hohen Aufwand/Instabilität.
                # Daher muss der Nutzer-Score invertiert werden, um Konsistenz zu schaffen.
                if cluster_var_name in ["Aufwand Zeit", "Aufwand Mobil", "Prozessinstabilität"]:
                    nutzer_cluster_variable_werte[cluster_var_name] = (5 - calculated_score) 
                else:
                    nutzer_cluster_variable_werte[cluster_var_name] = calculated_score
            else:
                nutzer_cluster_variable_werte[cluster_var_name] = float('nan') 

    # Filtere NaN-Werte heraus, da sie nicht in die Distanzberechnung einfließen sollen
    nutzer_cluster_variable_werte_filtered = {k: v for k, v in nutzer_cluster_variable_werte.items() if not np.isnan(v)}

    if not nutzer_cluster_variable_werte_filtered:
        return "Bitte bewerten Sie genügend Kriterien für die Clusterzuordnung (einschließlich der direkten Abfragen).", {}
    
    # Optional: Eine Mindestanzahl an bewerteten Cluster-Variablen sicherstellen
    MIN_CLUSTER_VARS_SCORED = 7 # z.B. mindestens 7 der 11 Cluster-Variablen müssen bewertet sein
    if len(nutzer_cluster_variable_werte_filtered) < MIN_CLUSTER_VARS_SCORED:
        return f"Bitte bewerten Sie mindestens {MIN_CLUSTER_VARS_SCORED} relevante Kriterien-Sets (Cluster-Variablen) für eine präzise Clusterzuordnung. Aktuell sind {len(nutzer_cluster_variable_werte_filtered)} bewertet.", {}


    # 3. Berechne die Abweichung des Nutzerprofils von jedem Clusterprofil
    abweichungen = {}
    for cluster_name, cluster_profil_werte in cluster_item_values.items():
        diffs = []
        for cluster_var_name, nutzer_wert in nutzer_cluster_variable_werte_filtered.items():
            if cluster_var_name in cluster_profil_werte: # Sicherstellen, dass die Variable auch im Cluster-Profil vorhanden ist
                diffs.append(abs(nutzer_wert - cluster_profil_werte[cluster_var_name]))
        
        if diffs:
            abweichungen[cluster_name] = np.mean(diffs)
        else:
            # Falls für ein Cluster keine vergleichbaren Variablen bewertet wurden, ist die Abweichung unendlich
            abweichungen[cluster_name] = float('inf') 

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
if "num_cnc_machines_categorized" not in st.session_state:
    st.session_state.num_cnc_machines_categorized = np.nan

# Automatisierungsgrad
if "automation_range" not in st.session_state:
    st.session_state.automation_range = None
if "num_auto_machines_categorized" not in st.session_state:
    st.session_state.num_auto_machines_categorized = np.nan

# Losgröße
if "losgroesse_range" not in st.session_state:
    st.session_state.losgroesse_range = None
if "losgroesse_categorized" not in st.session_state:
    st.session_state.losgroesse_categorized = np.nan

# Durchlaufzeit
if "durchlaufzeit_range" not in st.session_state:
    st.session_state.durchlaufzeit_range = None
if "durchlaufzeit_categorized" not in st.session_state:
    st.session_state.durchlaufzeit_categorized = np.nan

# Laufzeit
if "laufzeit_range" not in st.session_state:
    st.session_state.laufzeit_range = None
if "laufzeit_categorized" not in st.session_state:
    st.session_state.laufzeit_categorized = np.nan

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
    Dieser Readiness-Check dient der systematischen Erfassung des betrieblichen Reifegrads zur Einführung mobiler und zeitflexibler Arbeit in der zerspanenden Fertigung.

    Er basiert auf den vier arbeitswissenschaftlichen Gestaltungsdimensionen des MTOK-Modells – **Mensch**, **Technik**, **Organisation** und **Kultur** – und differenziert diese in insgesamt neun empirisch fundierte Handlungsfelder.

    Für jedes Handlungsfeld beantworten Sie eine Reihe von Bewertungskriterien anhand einer standardisierten 4-Punkte-Skala:

    - **1 = niedrig** – aktuell nicht erfüllt 
    - **2 = mittel** – in Ansätzen erfüllt 
    - **3 = hoch** – weitgehend umgesetzt 
    - **4 = sehr hoch** – vollständig umgesetzt und etabliert 

    Nach der Eingabe erhalten Sie ein grafisches Readiness-Profil sowie individuelle Handlungsempfehlungen auf Basis Ihrer Angaben.
    """)

elif current_tab in mtok_structure:
    dimension = current_tab
    for feld in mtok_structure[dimension]:
        st.subheader(f"Handlungsfeld: {feld}")
        scores_for_this_hf = [] # Temporäre Liste für die Bewertungen der Fragen in diesem Handlungsfeld
        for idx, item in enumerate(Kriterien.get(feld, [])):
            item_full_question_text = item['frage'] # Der volle Fragetext ist der Schlüssel für das Item-Mapping
            
            st.markdown(f"**{item_full_question_text}**")
            st.markdown(f"<span style='color:gray; font-size:0.9em'>{item['begründung']}</span>", unsafe_allow_html=True)
            
            # Eindeutiger Schlüssel für das individuelle Radio-Button-Element
            radio_key = f"{dimension}_{feld}_{idx}" 
            
            # Hole den gespeicherten Wert, falls vorhanden, sonst None
            initial_value = st.session_state.get(radio_key, None)
            
            # Finde den Index des initialen Wertes für st.radio
            try:
                # np.nan muss als None behandelt werden, da index() dies nicht verarbeiten kann
                default_index = [1, 2, 3, 4].index(initial_value) if initial_value is not None else None
            except ValueError:
                default_index = None # Fallback, wenn initial_value nicht in der Liste ist
                
            score = st.radio(
                "Bitte bewerten:",
                [1, 2, 3, 4],
                horizontal=True,
                key=radio_key,
                index=default_index # Setze den initialen Wert
            )
            
            if score is not None:
                # Speichere die individuelle Bewertung im session_state
                score_key = f"{radio_key}_score"
                st.session_state[score_key] = score
                scores_for_this_hf.append(score)
            else:
                scores_for_this_hf.append(np.nan) # Füge NaN hinzu, wenn nicht bewertet

        # Berechne den Mittelwert für das aktuelle Handlungsfeld (nur aus tatsächlich bewerteten Scores)
        # und speichere ihn in st.session_state.ergebnisse
        if any(~np.isnan(scores_for_this_hf)):
            st.session_state.ergebnisse[feld] = np.nanmean(scores_for_this_hf)
        elif feld in st.session_state.ergebnisse: # Wenn keine bewerteten Scores und Handlungsfeld schon da war
            del st.session_state.ergebnisse[feld] # Entferne es, um Konsistenz zu gewährleisten


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

   # Anzahl CNC-Werkzeugmaschinen
    cnc_options = ["< 5", "5 - 10", "11 - 24", "≥ 25"]
    selected_cnc_range = st.radio("Wie viele CNC-Werkzeugmaschinen haben Sie in Ihrer zerspanenden Fertigung?", cnc_options, key="cnc_range")
    st.session_state["anzahl_cnc-werkzeugmaschinen_categorized"] = categorize_cnc_machines(selected_cnc_range)
   

    # Automatisierungsgrad
    automation_percentage_options = ["0%", "1 - 25%", "26 - 49%", "≥ 50%"]
    selected_automation_range = st.radio("Wie viel Prozent Ihrer CNC-Werkzeugmaschinen besitzen eine Automation für den Werkstückwechsel?", automation_percentage_options, key="automation_range")
    st.session_state["automatisierungsgrad_categorized"] = categorize_automation_percentage(selected_automation_range)
    

    # Losgröße
    losgroesse_options = ["<5", "5–50", "51–99", "≥ 100"]
    selected_losgroesse = st.radio("Welche durchschnittlichen Losgrößen werden bei Ihnen gefertigt?", losgroesse_options, key="losgroesse_range")
    st.session_state["losgröße_categorized"] = categorize_losgroesse(selected_losgroesse)
    

    # Durchlaufzeit
    durchlaufzeit_options = ["< 10 min", "11–30 min", "31–89 min", "≥ 90 min"]
    selected_durchlaufzeit = st.radio("Wie lang ist die durchschnittliche Durchlaufzeit (von Rohmaterial bis zum unentgrateten Fertigteil) eines Auftrags über alle Maschinen?", durchlaufzeit_options, key="durchlaufzeit_range")
    st.session_state["durchlaufzeit_categorized"] = categorize_durchlaufzeit(selected_durchlaufzeit)
    

    # Laufzeit
    laufzeit_options = ["< 1 Tag", "1–3 Tage", "4–6 Tage", "≥ 7 Tage"]
    selected_laufzeit = st.radio("Welche durchschnittliche Laufzeit haben die Werkstücke, welche bei Ihnen gefertigt werden?", laufzeit_options, key="laufzeit_range")
    st.session_state["laufzeit_categorized"] = categorize_laufzeit(selected_laufzeit)
   
    st.text_input("PLZ (optional)", key="plz_input") # Eindeutiger Key
    st.text_input("E-Mail (optional)", key="email_input") # Eindeutiger Key
    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")

# Auswertungs-Tab
elif current_tab == "Auswertung":
    # Sicherstellen, dass alle benötigten Daten verfügbar sind, bevor der Knopf angezeigt wird
    if st.session_state.get('ergebnisse') and st.session_state.ergebnisse:
        # Hier die Logik zum Anzeigen des Radar-Diagramms und der Cluster-Zuordnung
        # (Dies ist der Teil, der ausgeführt wird, sobald der Benutzer auf den Reiter "Auswertung" wechselt)

        labels = []
        values = []
        for dim_name, handlungsfelder_in_dim in mtok_structure.items():
            for hf_name in handlungsfelder_in_dim:
                if hf_name in st.session_state.ergebnisse and st.session_state.ergebnisse[hf_name] is not None:
                    labels.append(f"{hf_name}\n({dim_name})")
                    values.append(st.session_state.ergebnisse[hf_name])

        radar_chart_fig = None
        if values:
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            values_cycle = values + values[:1]
            angles_cycle = angles + angles[:1]

            radar_chart_fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
            ax.fill(angles_cycle, values_cycle, color='cornflowerblue', alpha=0.3)
            ax.plot(angles_cycle, values_cycle, color='royalblue', linewidth=2)
            ax.set_yticks([1, 2, 3, 4])
            ax.set_yticklabels(['1 = Niedrig', '2 = Mittel', '3 = Hoch', '4 = Sehr hoch'], fontsize=8)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_title("Readiness-Profil – Mittelwerte nach Handlungsfeld", fontsize=14, pad=20)
            st.pyplot(radar_chart_fig) # Zeige das Diagramm an

        # Cluster-Zuordnung anzeigen
        cluster_result, abweichungen_detail = berechne_clusterzuordnung(Kriterien)
        
        display_cluster_result = ""
        if isinstance(cluster_result, str) and "Bitte bewerten Sie" in cluster_result:
            st.warning(cluster_result)
            display_cluster_result = cluster_result # Speichere Fehlermeldung
            # Hier keine weitere Auswertung, wenn Clusterzuordnung fehlschlägt
        else:
            st.subheader("Automatische Clusterzuordnung")
            st.success(f"Der Betrieb wird dem folgenden Cluster zugeordnet:\n\n**{cluster_result}**")
            display_cluster_result = cluster_result # Speichere erfolgreichen Cluster-Namen

            # GPT-Auswertung anzeigen
            st.subheader("Individuelle, KI-gestützte Handlungsempfehlung")
            with st.spinner("Die Handlungsempfehlungen werden generiert..."):
                gpt_output_text = frage_chatgpt_auswertung(st.session_state.ergebnisse, cluster_result)
            st.markdown(gpt_output_text)

            # --- PDF-Generierung und Download-Button ---
            # Sicherstellen, dass alle Teile für die PDF-Generierung verfügbar sind
            if radar_chart_fig and gpt_output_text and display_cluster_result:
                
                # Hier muss die Funktion generate_evaluation_pdf die tatsächlichen Mittelwerte der HF übergeben bekommen
                # die gpt_output_text, den cluster_result und das radar_chart_fig
                
                pdf_output_buffer = generate_evaluation_pdf(
                    st.session_state.ergebnisse,
                    display_cluster_result,
                    gpt_output_text,
                    radar_chart_fig,
                    mtok_structure # Struktur für die Tabelle der Mittelwerte
                )
                
                st.download_button(
                    label="Auswertung als PDF herunterladen",
                    data=pdf_output_buffer,
                    file_name="Readiness_Check_Auswertung.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("Nicht alle Daten für die PDF-Generierung verfügbar. Bitte füllen Sie alle Schritte aus.")

# --- Hier kommt der Rest des Streamlit Codes ---
# (Das gehört nicht zum Auswertungs-Tab, ist aber Teil der kompletten App)

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
