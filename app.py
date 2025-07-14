import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai # type: ignore
import streamlit.components.v1 as components

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
      "begründung": "Ein breites Aufgabenverständnis fördert Eigenverantwortung und unterstützt mobile Arbeitsformen."
    },
    {
      "frage": "M1.5 Beschäftigte lösen Störungen eigenständig.",
      "begründung": "Flexibles Arbeiten erfordert Handlungssicherheit bei Prozessabweichungen ohne direkte Unterstützung."
    },
    {
      "frage": "M1.6 Die Arbeitsumgebung ermöglicht produktives Arbeiten außerhalb der Fertigung.",
      "begründung": "Ergonomische, digitale und akustische Bedingungen sichern Leistung auch bei räumlicher Entkopplung."
    },
    {
      "frage": "M1.7 Erfahrungswissen wird dokumentiert und weitergegeben.",
      "begründung": "Wissenstransfer sichert Qualität und Anschlussfähigkeit bei wechselnden Präsenzzeiten."
    },
    {
      "frage": "M1.8 Beschäftigte erhalten gezielte Qualifizierungen zu mobilen und zeitflexiblen Arbeitsformen.",
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
      "begründung": "Digitale Anwendungskompetenz ist grundlegend für effektive Kollaboration."
    },
    {
      "frage": "M2.6 Beschäftigte verfügen über stabile externe Bedingungen für mobiles Arbeiten.",
      "begründung": "Rückzugsorte und unterstützendes Umfeld sind entscheidend für die Umsetzbarkeit."
    },
    {
      "frage": "M2.7 Beschäftigte bringen aktiv Verbesserungsvorschläge ein.",
      "begründung": "Beteiligung fördert die Passung und Akzeptanz flexibler Konzepte."
    },
    {
      "frage": "M2.8 Beschäftigte verstehen digitale Produktionssysteme in ihren Grundfunktionen.",
      "begründung": "Systemverständnis erhöht Handlungssicherheit und reduziert Fehlbedienungen."
    }
  ],
   "Arbeitsplatzgestaltung und Automatisierung": [
    {
    "frage": "T1.1 Die Werkzeugmaschine kann ohne ständige Anwesenheit betrieben werden (z. B. durch lange Laufzeiten oder automatisierte Routinetätigkeiten wie Werkstückhandling).",
    "begründung": "Ein hoher Automatisierungsgrad oder lange unbeaufsichtigte Laufzeiten ermöglichen zeitliche Entkopplung und reduzieren Präsenzzwänge im Schichtbetrieb."
    },
    {
    "frage": "T1.2 Aufgaben entlang der Prozesskette sind hinsichtlich ihrer Präsenzbindung analysiert (z. B. Trennung von Vorbereitung, Rüsten, Fertigen, Prüfen).",
    "begründung": "Eine systematische Analyse der Tätigkeiten ermöglicht die gezielte Aggregation präsenzkritischer und mobiler Anteile – Grundlage flexibler Gestaltungsmöglichkeiten."
    },
    {
    "frage": "T1.3 Präsenzgebundene Aufgaben (z. B. Maschineneinrichtung) können gebündelt und zeitlich verdichtet ausgeführt werden.",
    "begründung": "Planbare Präsenzphasen reduzieren Unterbrechungen und erleichtern mobile Arbeitsanteile außerhalb dieser Kernzeiten."
    },
    {
    "frage": "T1.4 Tätigkeiten an Maschinenarbeitsplätzen sind flexibel zwischen Beschäftigten übertragbar (z. B. bei Vertretung, Mehrmaschinenbedienung).",
    "begründung": "Aufgabenübertragbarkeit schafft Spielräume bei Personalengpässen, fördert Vertretungsfähigkeit und wurde in Cluster 3 als förderlicher Faktor identifiziert."
    },
    {
    "frage": "T1.5 Maschinenbedienung erfolgt auf Basis standardisierter und dokumentierter Abläufe.",
    "begründung": "Standardisierung ermöglicht Übergaben, unterstützt mobile Anteile und erleichtert Schulung sowie Fernbedienung."
    },
    {
    "frage": "T1.6 Fertigungsprozesse sind stabil, wiederholgenau und störungsarm.",
    "begründung": "Prozessstabilität ist Voraussetzung für entkoppelte Arbeitsformen und reduziert unvorhergesehene Eingriffe bei physischer Abwesenheit."
    },
    {
    "frage": "T1.7 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert (z. B. Kameras, Monitoring-Apps, Maschinenzugriff).",
    "begründung": "Sensorische oder visuelle Fernkontrolle reduziert Präsenznotwendigkeit und erlaubt situatives Eingreifen."
    },
    {
    "frage": "T1.8 Prüf- und Qualitätssicherungsprozesse sind automatisiert oder organisatorisch entkoppelt.",
    "begründung": "Entkoppelte Qualitätssicherung reduziert feste Rückmeldepunkte im Prozess und ermöglicht flexiblere Zeiteinteilung."
    },
    {
    "frage": "T1.9 Wartungsbedarfe und Eingriffsprotokolle sind digital dokumentiert und zentral zugänglich.",
    "begründung": "Digitale Transparenz unterstützt Eigenverantwortung, Übergaben und hybride Zuständigkeiten."
    },
    {
    "frage": "T1.10 Echtzeitdaten zur Maschinenauslastung sind digital verfügbar (z. B. OEE-Analyse, Laufzeitanalyse).",
    "begründung": "Prozessdaten ermöglichen situationsabhängige Steuerung und Optimierung – auch bei variabler Anwesenheit."
    },
    {
    "frage": "T1.11 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden (z. B. ERP, MES, BDE).",
    "begründung": "Vernetzte Systeme sind Voraussetzung für ortsunabhängige Steuerung, Planung und Dokumentation."
    },
    {
    "frage": "T1.12 Die Auswirkungen flexibler Arbeit auf Produktivität, Qualität und Maschinenauslastung werden regelmäßig erfasst.",
    "begründung": "Systematische Erfolgskontrolle unterstützt kontinuierliche Verbesserung und Legitimation flexibler Arbeitsmodelle im Produktionskontext."
    }
   ],
   "IT-Systemlandschaft und digital vernetzte Infrastruktur": [
    {
      "frage": "T2.1 Die IT-Infrastruktur stellt geeignete mobile Endgeräte zur Verfügung (z. B. Laptops, Tablets).",
      "begründung": "Mobile Endgeräte bilden die technische Basis für ortsunabhängiges Arbeiten in produktionsnahen Tätigkeiten."
    },
    {
      "frage": "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich (z. B. über VPN oder cloudbasierte Plattformen).",
      "begründung": "Flexibles Arbeiten erfordert sicheren Zugang zu zentralen Anwendungen von außerhalb der Fertigung."
    },
    {
      "frage": "T2.3 Digitale Kommunikations- und Kollaborationstools (z. B. MS Teams, Slack) sind standardisiert verfügbar.",
      "begründung": "Digitale Tools ermöglichen dezentrale Abstimmung, Informationsaustausch und Teamkommunikation."
    },
    {
      "frage": "T2.4 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar.",
      "begründung": "Zuverlässiger IT-Support sichert technische Funktionsfähigkeit und reduziert Akzeptanzbarrieren."
    },
    {
      "frage": "T2.5 Zugriffskonzepte sind sicher, rollenbasiert und klar geregelt.",
      "begründung": "Rollenklarheit und Zugriffsschutz sind zentrale Voraussetzungen für digitale Zusammenarbeit."
    },
    {
      "frage": "T2.6 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
      "begründung": "Vernetzung fördert bereichsübergreifende Koordination und reduziert Medienbrüche in Echtzeitprozessen."
    },
    {
      "frage": "T2.7 Die IT-Systeme ermöglichen ortsunabhängige Einsicht in produktionsrelevante Echtzeitdaten (z. B. Maschinenstatus, Auftragsfortschritt).",
      "begründung": "Transparenz in Echtzeit erhöht Steuerungsfähigkeit und Flexibilität im Produktionsumfeld."
    },
    {
      "frage": "T2.8 Beschäftigte können über mobile Endgeräte sicher Rückmeldungen und Produktionsdaten erfassen (z. B. Störgründe, Fortschritt).",
      "begründung": "Digitale Rückmeldung ermöglicht dezentrale Steuerung, reduziert Medienbrüche und fördert Eigenverantwortung."
    },
    {
      "frage": "T2.9 Simulationen oder digitale Zwillinge werden zur Produktionsplanung und -steuerung eingesetzt.",
      "begründung": "Vorausschauende Modellierung verbessert Planbarkeit und Reaktionsfähigkeit im flexiblen Umfeld."
    }
    ],
    "Kommunikation, Kooperation und Zusammenarbeit": [
    {
      "frage": "O1.1 Zwischen den Arbeitsbereichen bestehen strukturierte Kanäle für den Wissenstransfer.",
      "begründung": "Ein stabiler Wissenstransfer erhöht die Resilienz und kompensiert personelle Ausfälle bei mobil-flexiblen Arbeitsformen."
    },
    {
      "frage": "O1.2 Relevante Informationen werden zeitnah, digital und adressatengerecht weitergegeben.",
      "begründung": "Eine effektive Kommunikation ist die Grundlage für dezentrale Koordination und schnelle Reaktionsfähigkeit."
    },
    {
      "frage": "O1.3 Kommunikationskanäle sind auch bei Schichtübergaben und Vertretungssituationen verlässlich nutzbar.",
      "begründung": "Gerade in der zerspanenden Fertigung mit häufigem Personalwechsel sichern zuverlässige Kanäle die Prozesskontinuität."
    },
    {
      "frage": "O1.4 Verbindliche Regeln zur Nutzung digitaler Kommunikationswege (z. B. VPN, Remote-Zugriffe) sind etabliert und bekannt.",
      "begründung": "Klar definierte Regeln stärken die Sicherheit, erhöhen die Verlässlichkeit und fördern die Akzeptanz digitaler Kommunikationsformen."
    },
    {
      "frage": "O1.5 Hybride Besprechungen (Präsenz und Remote) sind etabliert und technisch unterstützt.",
      "begründung": "Hybride Formate ermöglichen ortsunabhängige Teilhabe und stärken die Integration mobiler Beschäftigter."
     },
    {
      "frage": "O1.6 Neue Beschäftigte werden strukturiert in Kommunikations- und Kooperationsprozesse eingeführt.",
      "begründung": "Eine systematische Einarbeitung unterstützt die Integration in digitale und flexible Arbeitsabläufe."
    },
    {
      "frage": "O1.7 Beschäftigte wissen, welche Kommunikationskanäle im Störungsfall zu nutzen sind.",
      "begründung": "Klare Kommunikationswege sind essenziell für eine schnelle Reaktion auf Abweichungen in der Produktion."
    },
    {
      "frage": "O1.8 Die digitale Kommunikationskompetenz der Beschäftigten wird systematisch gefördert.",
      "begründung": "Mediensouveränität ist Voraussetzung für eine funktionierende digitale Zusammenarbeit in verteilten Teams."
    },
    {
      "frage": "O1.9 Die eingesetzten digitalen Tools unterstützen die Zusammenarbeit (z. B. durch gemeinsame Plattformen oder Schnittstellen).",
      "begründung": "Technologische Unterstützung erleichtert den Informationsaustausch und ermöglicht reibungslose Teamarbeit."
    },
    {
      "frage": "O1.10 Die Kommunikationsstrukturen ermöglichen auch asynchrone Zusammenarbeit (z. B. Aufgabenboards, Kommentarfunktionen).",
      "begründung": "Asynchrone Kommunikation schafft Flexibilität bei der zeitlichen Abstimmung und stärkt die Selbstorganisation."
    },
    {
      "frage": "O1.11 Bei Problemen in der Zielerreichung oder Koordination werden die Kommunikationsstrukturen gezielt angepasst.",
      "begründung": "Eine lernende Organisation reflektiert und verbessert regelmäßig ihre Kommunikationsprozesse zur Sicherstellung der Zielerreichung."
    },
    {
      "frage": "O1.12 Die Organisation reflektiert regelmäßig die Wirkung von Zeitautonomie auf die Zusammenarbeit und Kommunikation.",
      "begründung": "Zeitliche Flexibilität verändert Abstimmungsprozesse, deren Passung kontinuierlich überprüft werden muss."
    }
    ],
    "Soziokulturelle und organisatorische Umwelt": [
    {
      "frage": "O2.1 Der Betrieb verfügt über ausreichend qualifizierte Fachkräfte in der zerspanenden Fertigung.",
      "begründung": "Fachkräftesicherung ist die Grundlage produktiver Flexibilisierung. Ohne entsprechende Qualifikation scheitern mobile und zeitflexible Modelle bereits in der Umsetzung."
    },
    {
      "frage": "O2.2 Die Personalplanung berücksichtigt den flexiblen Einsatz über unterschiedliche Zeiten und Orte hinweg.",
      "begründung": "Eine vorausschauende Planung schafft Handlungsspielräume für orts- und zeitflexible Einsätze, insbesondere im Schichtsystem oder bei wechselnden Anforderungen."
    },
    {
      "frage": "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und zeitflexibler Arbeit.",
      "begründung": "Klare Regelungen schaffen Rechtssicherheit und Orientierung – empirisch insbesondere in Cluster 3 als förderlich beschrieben."
    },
    {
      "frage": "O2.4 Externe Anforderungen von Kunden, Lieferanten oder Partnern werden in der Flexibilitätsstrategie berücksichtigt.",
      "begründung": "Schnittstellen zu externen Akteuren müssen abgestimmt sein, damit flexible Arbeitsformen betrieblich und marktseitig umsetzbar sind."
    },
    {
      "frage": "O2.5 Rechtliche Rahmenbedingungen (z. B. Arbeitszeitgesetz, Datenschutz) sind bekannt und werden beachtet.",
      "begründung": "Rechtskonformität erhöht die Akzeptanz flexibler Arbeit und verhindert Unsicherheiten oder Fehlentwicklungen."
    },
    {
      "frage": "O2.6 Arbeitszeitmodelle sind in Planungs- und Steuerungssysteme integriert (z. B. MES, ERP).",
      "begründung": "Nur durch die Integration in digitale Systeme können flexible Modelle zuverlässig geplant, dokumentiert und gesteuert werden."
    },
    {
      "frage": "O2.7 Die Aufbau- und Ablauforganisation ist anpassungsfähig (z. B. bei Sonderaufträgen oder kurzfristigen Vertretungen).",
      "begründung": "Strukturelle Anpassungsfähigkeit ist Voraussetzung für spontane Reaktion und produktive Umsetzung von Flexibilität – insbesondere in Cluster 2 und 4 als Schwachstelle identifiziert."
    },
    {
      "frage": "O2.8 Die Verantwortung der Führungskräfte für die Umsetzung flexibler Arbeit ist eindeutig definiert.",
      "begründung": "Unklare Rollen behindern Fortschritt. Führungskräfte sind entscheidend für die Gestaltung, Steuerung und Akzeptanz flexibler Arbeitsformen."
    },
    {
      "frage": "O2.9 Zuständigkeiten und Vertretungsregelungen sind auch bei mobiler Arbeit klar definiert.",
      "begründung": "Eindeutige Verantwortlichkeiten sichern die Prozessstabilität bei ortsflexibler Arbeit und entlasten das Team."
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
      "begründung": "Eine differenzierte Analyse präsenzpflichtiger und mobil bearbeitbarer Tätigkeiten ist Grundlage für jede flexible Arbeitsgestaltung."
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
      "frage": "K1.6 Die Unternehmensführung lebt Flexibilität sichtbar vor.",
      "begründung": "Vorbildverhalten auf Leitungsebene beeinflusst kulturelle Normen und senkt Umsetzungsbarrieren."
    },
    {
      "frage": "K1.7 Flexible Arbeit ist als selbstverständlicher Bestandteil der betrieblichen Praxis etabliert.",
      "begründung": "Normalisierung von Flexibilität reduziert Widerstände und erhöht die organisatorische Anschlussfähigkeit."
    },
    {
      "frage": "K1.8 Es bestehen keine verdeckten Erwartungen an ständige Erreichbarkeit.",
      "begründung": "Kulturelle Entgrenzung gefährdet Erholung, Selbststeuerung und nachhaltige Nutzung flexibler Arbeitsformen."
    },
    {
      "frage": "K1.9 Unterschiedliche Arbeitsstile und -rhythmen werden anerkannt und integriert.",
      "begründung": "Individuelle Unterschiede fördern Anpassungsfähigkeit und stärken das kulturelle Verständnis für Diversität."
    },
    {
      "frage": "K1.10 Mobile Arbeit wird systematisch in Teamabstimmungen integriert.",
      "begründung": "Kulturelle Integration erfordert explizite Berücksichtigung dezentraler Arbeit in Kommunikationsprozesse."
    },
    {
      "frage": "K1.11 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
      "begründung": "Transparente Diskussion über Zielkonflikte stärkt Vertrauen und vermeidet dysfunktionale Idealisierungen."
    },
    {
      "frage": "K1.12 Kulturelle Barrieren bei der Einführung flexibler Arbeit werden systematisch erfasst und reflektiert.",
      "begründung": "Nur durch strukturiertes Feedback lassen sich kulturelle Hürden identifizieren und gezielt adressieren."
    }
    ],
   "Soziale Beziehungen und Interaktion": [
    {
      "frage": "K2.1 Die Unternehmensführung positioniert sich aktiv und sichtbar zugunsten flexibler Arbeitsformen.",
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
      "frage": "K2.6 Es existieren verbindliche Kommunikationsstandards im Team (z. B. Regeltermine, Reaktionszeiten).",
      "begründung": "Verlässliche Kommunikationsprozesse kompensieren informelle Interaktionen bei physischer Distanz."
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
      "frage": "K2.12 Unterschiedliche Bedürfnisse (z. B. Schichtsystem, Pflegeverantwortung) werden teamintern berücksichtigt.",
      "begründung": "Eine faire Berücksichtigung individueller Anforderungen fördert Akzeptanz und Zusammenhalt im Team."
    }
  ]
}

# Mappings vorbereiten
dim_map = {feld: dim for dim, felder in mtok_structure.items() for feld in felder}

# Tabs definieren
tab_names = ["Start"] + list(mtok_structure.keys()) + ["Abschließende Fragen", "Auswertung"]

# Session-Variablen initialisieren
if "ergebnisse" not in st.session_state:
    st.session_state.ergebnisse = {}

# Tab-Navigation ohne Rerun
selected_tab = st.radio(
    "Navigation",
    tab_names,
    index=0,
    key="navigation_tab",
    horizontal=True
)

# Aktuellen Tab anzeigen
st.markdown(f"## {selected_tab}")

# Oben anzeigen: Navigationspfad
st.markdown(" ➤ ".join([
    f"<b style='color:#1f77b4'>{name}</b>" if name == selected_tab else name
    for name in tab_names
]), unsafe_allow_html=True)

# Inhalt der Tabs
if selected_tab == "Start":
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

elif selected_tab in mtok_structure:
    dimension = selected_tab
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

elif selected_tab == "Abschließende Fragen":
    st.text_input("Branche", key="branche")
    st.radio("Mitarbeitende", ["1-9", "10-49", "50-199", "200-499", "500-1999", ">2000"], key="mitarbeitende")
    st.radio("Funktion", ["Geschäftsführung", "Leitung", "Fachkraft", "Produktion", "Sonstige"], key="funktion")
    st.text_input("PLZ (optional)", key="plz")
    st.text_input("E-Mail (optional)", key="email")
    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")

elif selected_tab == "Auswertung":
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
            elif avg >= 2.8:
                cluster = "Cluster 4 – Effizient, aber strukturell gehemmt"
            elif avg >= 2.0:
                cluster = "Cluster 2 – Produktionsstark, aber mobilitätsfern"
            else:
                cluster = "Cluster 1 – Traditionell und reaktiv"
            st.info(f"Der Betrieb gehört vermutlich zu {cluster}.")

            # GPT-Auswertung
            st.subheader("Individuelle, KI-gestützte Handlungsempfehlung")
            with st.spinner("Die Handlungsempfehlungen werden generiert..."):
                antwort = frage_chatgpt_auswertung(st.session_state.ergebnisse)
            st.markdown(antwort)

# Trenner unten
st.markdown("---")
