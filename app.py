import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import textwrap  
import re
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

#Google Sheet Verbindung

# Zugriff Secrets mit Goofle Verbindungen
#service_account_info = st.secrets["gcp_service_account"]

# Authentifizierung mit aktuellem Scope
#scope = ["https://www.googleapis.com/auth/spreadsheets"]
#credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)

# Autorisierung für Google Sheets
#client = gspread.authorize(credentials)

# Spreadsheet öffnen
#worksheet = client.open_by_key("1pPljjp03HAB7KM_Qk9B4IYnnx0NVuFMxV81qvD67B3g").worksheet("Tabellenblatt1")

@st.cache_resource
def get_worksheet():
    # Zugriff auf die Secrets
    service_account_info = st.secrets["gcp_service_account"]

    # Authentifizierung mit aktuellem Scope
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)

    # Autorisierung für Google Sheets
    client = gspread.authorize(credentials)

    # Spreadsheet öffnen
    return client.open_by_key("1pPljjp03HAB7KM_Qk9B4IYnnx0NVuFMxV81qvD67B3g").worksheet("Tabellenblatt1")

# worksheet global verwenden
worksheet = get_worksheet()

st.markdown("""
    <style>
        /* Bisherige Formatierungen (wie bei dir) */
        html, body, [class*="css"]  {
            font-size: 18px !important;
            line-height: 1.6;
        }

        div[data-baseweb="radio"] {
            margin-bottom: -10px !important;
        }

        .element-container:has([data-baseweb="radio"]) {
            margin-bottom: -5px !important;
        }

        .evaluation-section {
            margin-bottom: 2.2rem;
        }

        .evaluation-question {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 0.4rem;
            color: #222;
        }

        .evaluation-container {
            padding: 1rem 1.5rem;
            background-color: #f9f9f9;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #ddd;
        }

        .evaluation-title {
            font-size: 24px;
            font-weight: bold;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
            color: #333;
        }

        .evaluation-info {
            font-size: 16px;
            color: #444;
            margin-bottom: 1rem;
        }

        /* NEU: Bewertungskarten Stufe 1–4 */
        .stufe-box {
            border-radius: 0.5rem;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            color: #fff;
            font-weight: 500;
        }

        .stufe-1 {
            background-color: #e53935;  /* rot */
        }

        .stufe-2 {
            background-color: #fb8c00;  /* orange */
        }

        .stufe-3 {
            background-color: #fdd835;  /* gelb */
            color: #000;
        }

        .stufe-4 {
            background-color: #43a047;  /* grün */
        }
    </style>
""", unsafe_allow_html=True)
# Struktur der Anwendung

st.set_page_config(page_title="Modell zur Systematisierung flexibler Arbeit", layout="wide")
st.title("Modell zur Systematisierung flexibler Arbeit")
st.markdown(
    "#### Typisierung und Gestaltung mobiler und zeitflexibler Arbeit in der zerspanenden Fertigung"
)

# MTOK-Dimensionen und Handlungsfelder
mtok_structure = {
    "Mensch": ["Produktivität und Motivation", "Persönliches Umfeld"],
    "Technik": ["Arbeitsplatzgestaltung und Automatisierung", "IT-Systemlandschaft und digital vernetzte Infrastruktur"],
    "Organisation": ["Kommunikation, Kooperation und Zusammenarbeit", "Organisatorische Umwelt", "Produktionsorganisation"],
    "Kultur": ["Unternehmenskultur", "Soziale Beziehungen und Interaktion"]
}

# Kriterienliste
Kriterien = {
  "Produktivität und Motivation": [
    {
      "frage": "M1.1 Im Unternehmen werden die Anforderungen an mobile Arbeit systematisch vermittelt (z. B. durch Schulungen, Leitfäden).",
      "begründung": "Mobile Arbeit setzt unteranderem sicheren IT-Zugang, Einbindung in digitale Prozesse und eigenverantwortliches Arbeiten voraus."
    },
    {
      "frage": "M1.2 Beschäftigte werden über Voraussetzungen und Grenzen zeitflexibler Arbeit informiert.",
      "begründung": "Nur wenn Beschäftigte die Voraussetzungen und Grenzen zeitflexibler Arbeit kennen, kann diese in der Zerspanung realistisch und störungsfrei umgesetzt werden."
    },
    {
      "frage": "M1.3 Es besteht ein erkennbares Interesse der Beschäftigten an mobilen und/oder zeitflexiblen Arbeitsmodellen (z.B. Mitarbeiterbefragungen, Verbesserungsvorschlägen).",
      "begründung": "Ein eigenständiges Engagement stärkt die Motivation für Veränderungsmaßnahmen."
    },
    {
      "frage": "M1.4 Im Unternehmen bestehen konkrete Angebote zur Qualifizierung der Beschäftigten im Hinblick auf mobile und zeitflexible Arbeitsmodelle.",
      "begründung": "Kompetenzaufbau fördert Motivation und langfristige Bindung an flexible Arbeitsmodelle."
    },
    {
      "frage": "M1.5 Beschäftigte verfügen über die notwendigen Kompetenzen zur eigenständigen, flexiblen Aufgabenbearbeitung.",
      "begründung": "Produktive flexible Arbeit erfordert eigenständige Prozesskontrolle, Informationsverarbeitung und Handlungssicherheit durch Qualifikation."
    },
    {
      "frage": "M1.6 Beschäftigte sind in der Lage, Prozessstörungen ohne direkte Unterstützung zu beheben.",
      "begründung": "Flexibles Arbeiten erfordert Handlungssicherheit bei Prozessabweichungen ohne direkte Unterstützung."
    },
    {
      "frage": "M1.7 Die Auswirkungen flexibler Arbeit auf die Produktivität werden regelmäßig analysiert und reflektiert",
      "begründung": "Eine systematische Rückkopplung zwischen Flexibilisierung und Produktivitätskennzahlen ist erforderlich, um Effizienzgewinne oder Zielkonflikte frühzeitig zu erkennen."
    }
  ],
  "Persönliches Umfeld": [
    {
      "frage": "M2.1 Beschäftigte zeigen Offenheit gegenüber mobiler Arbeit.",
      "begründung": "Eine positive Grundhaltung erleichtert den Einstieg in ortsunabhängiges Arbeiten."
    },
    {
      "frage": "M2.2 Beschäftigte zeigen Offenheit gegenüber zeitflexibler Arbeit.",
      "begründung": "Offenheit unterstützt die Akzeptanz variabler Arbeitszeiten."
    },
    {
      "frage": "M2.3 Beschäftigte wurden gezielt auf flexible Arbeit vorbereitet (z.B. Einarbeitungspläne, Workshops).",
      "begründung": "Vorbereitung erhöht Selbstwirksamkeit und Engagement."
    },
    {
      "frage": "M2.4 Beschäftigte identifizieren sich mit ihrer Tätigkeit und dem Unternehmen.",
      "begründung": "Hohe Identifikation stärkt Eigenverantwortung und Leistungsbereitschaft."
    },
    {
      "frage": "M2.5 Beschäftigte haben regelmäßig die Möglichkeit, Verbesserungsvorschläge zu flexibler Arbeit einzubringen.",
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
      "frage": "M2.8 Beschäftigte stehen offen und veränderungswillig gegenüber digital vernetzten Technologien und Abläufen.",
      "begründung": "Technikakzeptanz ist eine zentrale Voraussetzung für Vertrauen in digitale Lösungen und mobile Prozesse."
    }
  ],
   "Arbeitsplatzgestaltung und Automatisierung": [
    {
    "frage": "T1.1 Fertigungsprozesse sind störungsarm.",
    "begründung": "Prozessstabilität ist Voraussetzung für flexible Arbeitsmodelle und reduziert unvorhergesehene Eingriffe bei physischer Abwesenheit."
    },
    {
    "frage": "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
    "begründung": "Ein hoher Automatisierungsgrad oder lange unbeaufsichtigte Laufzeiten ermöglichen zeitliche Entkopplung und reduzieren Präsenzzwänge."
    },
    {
    "frage": "T1.3 Die Arbeitsplatzgestaltung ermöglicht ein produktives Zusammenarbeiten mit Beschäftigten außerhalb der Fertigung.",
    "begründung": "Der Maschinenarbeitsplatz oder getrennte Räumlichkeiten ermöglichen eine produktive Kooperation mit mobil arbeitenden Beschäftigten."
    },
    {
    "frage": "T1.4 Werkzeuge und Betriebsmittel sind digital erfasst und ortsunabhängig verfügbar.",
    "begründung": "Digitale Werkzeug- und Betriebsmitteldatenbanken ermöglichen schnelle Informationsverfügbarkeiten, unterstützt flexible Einsatzplanung und reduziert Präsenzzeiten bei der Vorbereitung und Nutzung."
    },
    {
    "frage": "T1.5 Produktionsprozesse sind standardisiert dokumentiert und übertragbar.",
    "begründung": "Standardisierung erleichtert Vertretungen, Übergaben und mobile Unterstützungsformate."
    },
    {
    "frage": "T1.6 Echtzeitdaten zu Prozessen sind digital verfügbar.",
    "begründung": "Prozessdaten (z. B. OEE-Analyse, Laufzeitanalyse) ermöglichen auch bei variabler Anwesenheit situationsabhängige Steuerung und Optimierung."
    },
    {
    "frage": "T1.7 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
    "begründung": "Vernetzte Systeme (z. B. ERP, MES, BDE) sind Voraussetzung für ortsunabhängige Steuerung, Planung und Dokumentation."
    },
    {
    "frage": "T1.8 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert.",
    "begründung": "Sensorische oder visuelle Fernkontrolle (z. B. Kameras, Monitoring-Apps, Maschinenzugriff) reduziert Präsenznotwendigkeit und erlaubt situatives Eingreifen."
    },
    {
    "frage": "T1.9 Methoden zur regelmäßigen Erfassung potenzieller Auswirkungen flexibler Arbeit existieren.",
    "begründung": "Systematische Erfolgskontrolle (z. B. auf Produktivität, Qualität, Maschinenauslastung) unterstützt kontinuierliche Verbesserung und Legitimation flexibler Arbeitsmodelle im Produktionsbereich."
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
      "frage": "T2.3 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar und kann auch produktionsbezogene IT-Probleme beheben.",
      "begründung": "Zuverlässiger IT-Support sichert technische Funktionsfähigkeit und reduziert Akzeptanzbarrieren."
    },
    {
      "frage": "T2.4 Digitale Kommunikations- und Kollaborationstools sind standardisiert verfügbar.",
      "begründung": "Digitale Tools ermöglichen dezentrale Abstimmung, Informationsaustausch und Teamkommunikation."
    },
    {
      "frage": "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
      "begründung": "Vernetzung fördert bereichsübergreifende Koordination und reduziert Medienbrüche in Echtzeitprozessen.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "T2.6 IT-Sicherheitskonzepte sind etabliert, werden regelmäßig geprüft und gewährleisten den Schutz vor externen Angriffen und Datenverlust.",
      "begründung": "Robuste IT-Sicherheitsmaßnahmen (z. B. VPN-Verbindungen) sind fundamental für den Schutz sensibler Produktions- und Unternehmensdaten und zur Aufrechterhaltung der Betriebskontinuität bei flexibler Arbeit."
    }
    ],
    "Kommunikation, Kooperation und Zusammenarbeit": [
    {
      "frage": "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
      "begründung": "Effektiver Informationsfluss ist essenziell für dezentrale Koordination, schnelle Reaktionen und Ausfallkompensation."
    },
    {
      "frage": "O1.2 Konzepte zur Förderung digitaler Kommunikationskompetenz und zur strukturierten Einarbeitung in Kooperationsprozesse sind etabliert.",
      "begründung": "Digitale Souveränität und fundierte Einarbeitung sichern Zusammenarbeit und Akzeptanz in verteilten Teams."
    },
    {
      "frage": "O1.3 Erfahrungswissen wird systematisch dokumentiert, digital zugänglich gemacht und aktiv weitergegeben.",
      "begründung": "Strukturierter Wissenstransfer (z. B. Best Practices) fördert Qualität, Lernen und Unabhängigkeit."
    },
    {
      "frage": "O1.4 Verantwortlichkeiten sind eindeutig geregelt, relevante Akteure (z. B. Betriebsrat, Datenschutz) sind aktiv eingebunden.",
      "begründung": "Klare Rollen und partizipative Gestaltung stärken Rechtssicherheit und Akzeptanz."
    }
    ],
    "Organisatorische Umwelt": [
    {
      "frage": "O2.1 Im Unternehmen stehen ausreichend qualifizierte Fachkräfte für die zerspanende Fertigung zur Verfügung.",
      "begründung": "Fachkräftesicherung ist die Grundlage produktiver Flexibilisierung. Ohne entsprechende Qualifikation scheitern mobile und zeitflexible Modelle bereits in der Umsetzung."
    },
    {
      "frage": "O2.2 Rechtliche Rahmenbedingungen flexibler Arbeit sind im Unternehmen bekannt und werden berücksichtigt.",
      "begründung": "Rechtskonformität (z. B. Arbeitszeitgesetz, Datenschutz) erhöht die Akzeptanz flexibler Arbeit und verhindert Unsicherheiten oder Fehlentwicklungen."
    },
    {
      "frage": "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und/oder zeitflexibler Arbeit.",
      "begründung": "Klare Regelungen schaffen Rechtssicherheit, Orientierung und Transparenz für Beschäftigte und Führungskräfte.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.4 Externe Anforderungen (z. B. Kunden, Lieferanten, Partner) werden bei der Gestaltung flexibler Arbeit berücksichtigt.",
      "begründung": "Eine abgestimmte Schnittstellengestaltung mit externen Akteuren ist notwendig, damit flexible Arbeitsmodelle betrieblich und marktseitig umsetzbar bleiben."
    },
    {
      "frage": "O2.5 Die Personalplanung berücksichtigt flexible Arbeitszeiten und ist technisch im Planungssystem abbildbar.",
      "begründung": "Flexible Arbeitszeiten erfordern organisatorische Offenheit und eine digitale Integration in Systeme wie MES oder ERP, um verlässliche Steuerung und Dokumentation zu ermöglichen.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.6 Die Personalplanung berücksichtigt flexible Arbeitsorte und ist technisch im Planungssystem abbildbar.",
      "begründung": "Mobile Arbeit erfordert eine systemische Einbindung in Planungstools, um ortsunabhängige Einsätze koordinieren und dokumentieren zu können.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.7 Verantwortlichkeiten für die Einführung und den operativen Alltag flexibler Arbeitsmodelle sind klar geregelt.",
      "begründung": "Klare strategische und operative Zuständigkeiten sind notwendig, um flexible Arbeitsmodelle dauerhaft verlässlich umzusetzen."
    },
    {
      "frage": "O2.8 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten.",
      "begründung": "Die Möglichkeit zur Mitgestaltung ist empirisch als signifikanter Einflussfaktor für erfolgreiche Flexibilisierung belegt."
    },
    {
      "frage": "O2.9 Pausenregelungen lassen zeitliche Flexibilität im Rahmen betrieblicher Vorgaben zu.",
      "begründung": "Flexible Pausengestaltung erhöht Erholungseffekte, fördert Selbstbestimmung und verbessert individuelle Leistungssteuerung."
    },
    {
      "frage": "O2.10 Arbeitszeitkonten oder vergleichbare Instrumente werden aktiv zur Steuerung flexibler Arbeitszeiten genutzt.",
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
      "begründung": "Kleinere oder mittlere Losgrößen erhöhen die Dispositionsfreiheit und ermöglichen eine flexiblere Einsatzplanung."
    },
    {
    "frage": "O3.3 Lauf- und Durchlaufzeiten sind planbar und stabil steuerbar.",
      "begründung": "Planbare Prozesszeiten schaffen Handlungssicherheit und ermöglichen eine verlässliche Integration flexibler Arbeitszeitmodelle."
    },
    {
    "frage": "O3.4 Die Personaleinsatzplanung berücksichtigt Puffer zur Kompensation von Engpässen.",
      "begründung": "Gezielte Pufferplanung (z. B. Springer, Reservezeiten) ermöglicht individuelle Flexibilität ohne Produktivitätseinbußen."
    },
    {
    "frage": "O3.5 Qualitätssicherungsprozesse sind automatisiert unterstützt und kontinuierlich wirksam.",
      "begründung": "Automatisierte Prüfverfahren (z. B. Inline-Messung, Prozessüberwachung) reduzieren manuelle Kontrollaufwände und ermöglichen flexiblere Zeiteinteilung."
    },
    {
    "frage": "O3.6 Operative Führungskräfte können dezentral Anpassungen in der Steuerung vornehmen.",
      "begründung": "Dezentrale Entscheidungskompetenz erhöht Reaktionsfähigkeit bei sich ändernden Anwesenheiten und Aufgabenverteilungen."
    },
    {
      "frage": "O3.7 Kurzfristige Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten.",
      "begründung": "Technische oder organisatorische Toleranzen (z. B. Pufferzeiten, redundante Maschinen) ermöglichen flexible Abwesenheiten und schaffen Spielräume für Zeitautonomie."
    },
    {
      "frage": "O3.8 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
      "begründung": "Digitale Vernetzung und Flexibilität der Steuerung ermöglichen schnelle Reaktionen auf sich ändernde Rahmenbedingungen."
    },
    {
      "frage": "O3.9 Simulationen werden aktiv zur Produktionsplanung und -steuerung eingesetzt.",
      "begründung": "Vorausschauende Simulationsmodelle (z. B. Auslastung, Fertigungsprozess) verbessern Planbarkeit und erhöhen die Robustheit flexibler Arbeitsorganisation."
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
    "frage": "K1.4 Fehler im Umgang mit flexiblen Arbeitsmodellen werden offen thematisiert und als Lernchance genutzt.",
      "begründung": "Eine konstruktive Fehlerkultur fördert Anpassungsfähigkeit, Lernprozesse und Innovationskraft bei der Einführung flexibler Modelle."
    },
    {
      "frage": "K1.5 Erwartungen an dauerhafte Erreichbarkeit sind klar geregelt und werden aktiv begrenzt.",
      "begründung": "Klare Grenzen zur Erreichbarkeit stärken Erholung, Selbststeuerung und die nachhaltige Nutzung flexibler Arbeitsmodelle."
    },
    {
      "frage": "K1.6 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
      "begründung": "Transparente Diskussion über Zielkonflikte stärkt Vertrauen und vermeidet dysfunktionale Idealisierungen."
    },
    {
      "frage": "K1.7 Prozesse zur systematischen Erfassung und Reflexion potenzieller kultureller Barrieren bei der Einführung flexibler Arbeit existieren.",
      "begründung": "Nur durch strukturiertes Feedback lassen sich kulturelle Hürden identifizieren und gezielt adressieren"
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
      "frage": "K2.6 Die Zielsetzung und Zusammenarbeit im Team werden regelmäßig gemeinsam reflektiert.",
      "begründung": "Reflexion fördert kontinuierliche Weiterentwicklung, stärkt Selbststeuerung und verbessert die Teamleistung."
    },
    {
      "frage": "K2.7 Teammitglieder kennen ihre Rollen und Verantwortlichkeiten.",
      "begründung": "Klare Rollenklarheit erhöht Handlungssicherheit und reduziert Koordinationsaufwand."
    },
    {
      "frage": "K2.8 Konflikte im Team werden frühzeitig erkannt und durch geeignete Prozesse oder Moderation gelöst.",
      "begründung": "Ein strukturierter Umgang mit Konflikten erhöht die Stabilität flexibler Arbeitsmodelle und stärkt das Vertrauen."
    },
    {
      "frage": "K2.9 Individuelle Arbeitsstile und -rhythmen werden respektiert und in die Teamprozesse eingebunden.",
      "begründung": "Diese Anerkennung fördert flexible Zusammenarbeit und steigert die Teamzufriedenheit."
    }
  ]
    }

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
    if losgroesse_str is None:
        return np.nan
    mapping = {
        "< 5": 1,
        "5-50": 2,
        "51-99": 3,
        "≥ 100": 4
    }
    return mapping.get(losgroesse_str, np.nan)

def categorize_durchlaufzeit(durchlaufzeit_str):
    if durchlaufzeit_str is None:
        return np.nan
    mapping = {
        "< 10 min": 1,
        "11–30 min": 2,
        "31–89 min": 3,
        "≥ 90 min": 4
    }
    return mapping.get(durchlaufzeit_str, np.nan)

def categorize_laufzeit(laufzeit_str):
    if laufzeit_str is None:
        return np.nan
    mapping = {
        "< 1 Tag": 1,
        "1–3 Tage": 2,
        "4–6 Tage": 3,
        "≥ 7 Tage": 4
    }
    return mapping.get(laufzeit_str, np.nan)

kriterien_item_to_cluster_variable_mapping = {
       
    # 1. Automatisierungsgrad (Wert kommt direkt aus "Abschließende Fragen")
    # 2. Anzahl CNC-Werkzeugmaschinen (Wert kommt direkt aus "Abschließende Fragen")
    # 3. Losgröße (Wert kommt direkt aus "Abschließende Fragen")
    # 4. Durchlaufzeit (Wert kommt direkt aus "Abschließende Fragen")
    # 5. Laufzeit (Wert kommt direkt aus "Abschließende Fragen")

    # 6. Digitalisierungsgrad
    "Digitalisierungsgrad": [
        "M2.7 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren Grundfunktionen.",
        "T1.7 Maschinenarbeitsplätze sind über Schnittstellen mit zentralen digitalen Systemen verbunden.",
        "T2.5 Digitale Schnittstellen zwischen Produktion, Planung und Führung sind etabliert.",
        "T2.4 Digitale Kommunikations- und Kollaborationstools sind standardisiert verfügbar.",
        "O2.5 Die Personalplanung berücksichtigt flexible Arbeitszeiten und ist technisch im Planungssystem abbildbar.",
        "O3.8 Die Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
        "O3.9 Simulationen werden aktiv zur Produktionsplanung und -steuerung eingesetzt.",
    ],
    
    # 7. Prozessinstabilität
    "Prozessinstabilität": [
        "T1.1 Fertigungsprozesse sind störungsarm.", # Niedriger Wert hier bedeutet hohe Instabilität (daher Skala invertiert für dieses Item bei Berechnung)
        "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
        "O1.2 Konzepte zur Förderung digitaler Kommunikationskompetenz und zur strukturierten Einarbeitung in Kooperationsprozesse sind etabliert.",
        "O3.7 Kurzfristige Maschinenstillstände führen nicht unmittelbar zu kritischen Produktivitätsverlusten.",
    ],
    
    # 8. Nutzen (Wahrgenommener Nutzen von Flexibilität)
    "Nutzen": [
        "T1.9 Methoden zur regelmäßigen Erfassung potenzieller Auswirkungen flexibler Arbeit existieren.",
        "K1.3 Zielerreichung hat Vorrang vor physischer Anwesenheit.",
        "K1.6 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
        "K2.2 Führungskräfte unterstützen aktiv flexible Arbeitsformen und fördern Eigenverantwortung im Team."
    ],
    
    # 9. Akzeptanz
    "Akzeptanz": [
        "M1.3 Es besteht ein erkennbares Interesse der Beschäftigten an mobilen und/oder zeitflexiblen Arbeitsmodellen (z.B. Mitarbeiterbefragungen, Verbesserungsvorschlägen).",
        "M1.7 Die Auswirkungen flexibler Arbeit auf die Produktivität werden regelmäßig analysiert und reflektiert",
        "M2.1 Beschäftigte zeigen Offenheit gegenüber mobiler Arbeit.",
        "M2.2 Beschäftigte zeigen Offenheit gegenüber zeitflexibler Arbeit.",
        "O2.3 Es bestehen verbindliche Betriebsvereinbarungen zur Regelung mobiler und/oder zeitflexibler Arbeit.",
        "K1.6 Zielkonflikte zwischen Flexibilität und Produktionssicherheit werden offen angesprochen.",
        "K2.1 Die Unternehmensführung positioniert sich aktiv und lebt Flexibilität sichtbar vor."
    ],
    
    # 10. Aufwand Zeit (Wahrgenommener Zeitaufwand für flexible Arbeit)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Wert inbvertiert, da ein höherer Score in der Frage ("können mitgestalten") einen niedrigeren "Aufwand Zeit" für das Cluster bedeutet.
    "Aufwand Zeit": [
        "M2.2 Beschäftigte zeigen Offenheit gegenüber zeitflexibler Arbeit.",
        "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "T2.6 IT-Sicherheitskonzepte sind etabliert, werden regelmäßig geprüft und gewährleisten den Schutz vor externen Angriffen und Datenverlust.",
        "O1.1 Informationen für Planung, Wissenstransfer, Schichtübergaben und Störfälle sind über verlässliche, digitale Kanäle zeitnah und adressatengerecht verfügbar.",
        "O2.5 Die Personalplanung berücksichtigt flexible Arbeitszeiten und ist technisch im Planungssystem abbildbar.",
        "O2.8 Beschäftigte können Beginn und Ende ihrer täglichen Arbeitszeit innerhalb eines definierten Rahmens mitgestalten."
    ],
    
    # 11. Aufwand Mobil (Wahrgenommener Aufwand für mobiles Arbeiten)
    # HINWEIS: Wird auch invertiert (Siehe Aufwand Zeit)
    "Aufwand Mobil": [
        "M1.1 Im Unternehmen werden die Anforderungen an mobile Arbeit systematisch vermittelt (z. B. durch Schulungen, Leitfäden).",
        "M2.1 Beschäftigte zeigen Offenheit gegenüber mobiler Arbeit.",
        "T1.1 Fertigungsprozesse sind störungsarm.",
        "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "T1.8 Fernüberwachung und Fernzugriff auf Maschinen ist technisch realisiert.",
        "T2.3 Der IT-Support ist auch bei mobiler Arbeit verlässlich erreichbar und kann auch produktionsbezogene IT-Probleme beheben.",
        "O1.2 Konzepte zur Förderung digitaler Kommunikationskompetenz und zur strukturierten Einarbeitung in Kooperationsprozesse sind etabliert.",
        "O3.1 Die Aufgaben sind hinsichtlich ihrer Präsenzbindung analysiert und systematisch aufteilbar."
    ]
}

# Clusterprofile aus empirischer Clustertabelle
cluster_item_values = {
    "Cluster 1 – Traditionell und reaktiv": {
        "Automatisierungsgrad": 2,
        "Anzahl CNC-Werkzeugmaschinen": 2,
        "Losgröße": 2,
        "Durchlaufzeit": 2,
        "Laufzeit": 2,
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 3, 
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3, 
        "Aufwand Mobil": 4 
    },
    "Cluster 2 – Produktionsstark, aber mobilitätsfern": {
        "Automatisierungsgrad": 3,
        "Anzahl CNC-Werkzeugmaschinen": 3,
        "Losgröße": 4,
        "Durchlaufzeit": 3,
        "Laufzeit": 1, 
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 2,
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3,
        "Aufwand Mobil": 4
    },
    "Cluster 3 – Digital-affin und akzeptanzstark": {
        "Automatisierungsgrad": 4,
        "Anzahl CNC-Werkzeugmaschinen": 2, 
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
    "Cluster 4 – Technisch solide, aber prozessual träge": {
        "Automatisierungsgrad": 2,
        "Anzahl CNC-Werkzeugmaschinen": 3, 
        "Losgröße": 2,
        "Durchlaufzeit": 4, 
        "Laufzeit": 3, 
        "Digitalisierungsgrad": 2,
        "Prozessinstabilität": 2,
        "Nutzen": 2,
        "Akzeptanz": 2,
        "Aufwand Zeit": 3,
        "Aufwand Mobil": 3
    }
}

#Berechnung der Clusterzuordnung

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

# Ende der Berechnungslogik

# Start des Streamlit UI Codes

# Initialisierung des aktuellen Tabs
if "current_tab_index" not in st.session_state:
    st.session_state.current_tab_index = 0

# Initialisierung der Ergebnisstruktur
if "ergebnisse" not in st.session_state:
    st.session_state.ergebnisse = {}

# Initialisierung des item_to_radio_key_map (für Cluster-Zuordnung)
if "item_to_radio_key_map" not in st.session_state:
    st.session_state.item_to_radio_key_map = {}

# Mapping von Textbewertung zu numerischen Score
score_mapping = {
    "Nicht erfüllt": 1,
    "Teilweise erfüllt": 2,
    "Weitestgehend erfüllt": 3,
    "Vollständig erfüllt": 4
}
        
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
tab_names = ["Start"] + list(mtok_structure.keys()) + ["Abschließende Fragen", "Auswertung","Evaluation"]

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

# Inhalt Start-Tabs

if current_tab == "Start":
    st.markdown("""
    <style>
        .stufe-box {
            padding: 0.9rem 1.2rem;
            border-radius: 0.6rem;
            border: 1px solid #ccc;
            background-color: #f8f8f8;
            margin-bottom: 1rem;
            font-size: 17px;
        }
        .stufe-1 { border-left: 5px solid #ff4d4d; }  /* Rot */
        .stufe-2 { border-left: 5px solid #ffaa00; }  /* Orange */
        .stufe-3 { border-left: 5px solid #ffd633; }  /* Gelb */
        .stufe-4 { border-left: 5px solid #28a745; }  /* Grün */
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    
        Die **Digitalisierung** und der **Wunsch nach flexibleren Arbeitsmodellen** stellen produzierende Unternehmen vor neue Herausforderungen. Wie können beispielsweise Homeoffice und flexible Arbeitszeiten in der Produktion umgesetzt werden? Das entwickelte Diagnose- und Entwicklungsmodell hilft Ihnen dabei, diese Frage systematisch anzugehen: Es zeigt Ihnen, wo Ihr Unternehmen heute steht und gibt Ihnen konkrete Handlungsempfehlungen für die Umsetzung flexibler Arbeitsformen an die Hand.
       
        Das Modell wurde speziell für **Unternehmen der zerspanenden Fertigung** entwickelt. Es ermöglicht Ihnen eine **strukturierte Bestandsaufnahme** Ihres Unternehmens und zeigt gleichzeitig auf, wie Sie die **Einführung mobiler und zeitflexibler Arbeit** unterstützen können. Dabei berücksichtigt das Modell vier wichtige Bereiche: Ihre Beschäftigten, die vorhandene Technik, Ihre Organisation und die Unternehmenskultur. Diese vier Bereiche werden in neun **konkrete Handlungsfelder** unterteilt, die speziell auf die Besonderheiten der zerspanenden Fertigung zugeschnitten sind.
    """)
        st.markdown('<p><strong>Die Bewertung basiert auf einem vierstufigen System:</strong></p>', unsafe_allow_html=True)

        st.markdown('<div class="stufe-box stufe-1">🔴 <strong>Stufe 1 – Nicht erfüllt:</strong> Dieses Kriterium wird derzeit nicht umgesetzt.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stufe-box stufe-2">🟠 <strong>Stufe 2 – Teilweise erfüllt:</strong> Erste Ansätze sind vorhanden, aber noch nicht systematisch.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stufe-box stufe-3">🟡 <strong>Stufe 3 – Weitgehend erfüllt:</strong> Das Kriterium ist größtenteils umgesetzt und funktioniert.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="stufe-box stufe-4">🟢 <strong>Stufe 4 – Vollständig erfüllt:</strong> Das Kriterium ist vollständig umgesetzt und fest etabliert.</div>', unsafe_allow_html=True)

    st.markdown("""    
        Nach der Selbstbewertung erhalten Sie ein übersichtliches **grafisches Profil**, das Ihre Stärken und Verbesserungsmöglichkeiten auf einen Blick zeigt. Das System ordnet Ihr Unternehmen automatisch einem von **vier Unternehmenstypen** zu, die aus der Praxis abgeleitet wurden. Basierend auf diesem Typem bekommen Sie maßgeschneiderte, praxisnahe Handlungsempfehlungen, die Ihnen konkrete nächste Schritte für die Weiterentwicklung Ihrer Arbeitsorganisation aufzeigen.
    """)

# Inhalt MTOK-Tabs

elif current_tab in mtok_structure:
    dimension = current_tab
    for feld in mtok_structure[dimension]:
        st.subheader(f"Handlungsfeld: {feld}")
        scores_for_this_hf = []

        for idx, item in enumerate(Kriterien.get(feld, [])):
            frage_text = item["frage"]
            begruendung = item["begründung"]

            st.markdown(f"""
                <div style='margin-bottom: -0.2rem'>
                    <strong>{frage_text}</strong><br>
                    <span style='color:gray; font-size:0.95em'>{begruendung}</span>
                </div>
            """, unsafe_allow_html=True)
           
            # Nutze indexbasierten Schlüssel (idx), damit die Zuordnung mit Kriterien stabil bleibt
            radio_key = f"{dimension}_{feld}_{idx}"
            score_key = f"{radio_key}_score"

            # Mapping zur späteren Auswertung
            if "item_to_radio_key_map" not in st.session_state:
                st.session_state["item_to_radio_key_map"] = {}
            st.session_state["item_to_radio_key_map"][item['frage']] = score_key
            
            # Bewertungsoptionen abhängig von Einschränkung
            einschraenkung = item.get("einschraenkung", None)
            if einschraenkung == "1_und_4":
                options = ["Nicht erfüllt", "Vollständig erfüllt"]
            else:
                options = ["Nicht erfüllt", "Teilweise erfüllt", "Weitestgehend erfüllt", "Vollständig erfüllt"]

            # Vorherige Auswahl als Text merken (Rückwärts-Mapping)
            vorhandene_zahl = st.session_state.get(score_key, None)
            if vorhandene_zahl in [1, 2, 3, 4]:
                reverse_mapping = {v: k for k, v in score_mapping.items()}
                initial_value = reverse_mapping.get(vorhandene_zahl)
            else:
                initial_value = None

            try:
                default_index = options.index(initial_value) if initial_value else 0
            except ValueError:
                default_index = 0

            auswahl = st.radio("", options, key=radio_key, index=default_index)

            # In Score umwandeln
            score = score_mapping.get(auswahl, np.nan)
            st.session_state[score_key] = score
            scores_for_this_hf.append(score)

        # Mittelwert pro Handlungsfeld
        if any(~np.isnan(scores_for_this_hf)):
            st.session_state.ergebnisse[feld] = np.nanmean(scores_for_this_hf)
        elif feld in st.session_state.ergebnisse:
            del st.session_state.ergebnisse[feld]
            
elif current_tab == "Abschließende Fragen":
    st.subheader("Spezifische technische und prozessuale Angaben")

    def radio_with_categorization(frage, options, key, categorize_func):
        # Hole bisherigen Wert aus dem Session State
        vorhandene_auswahl = st.session_state.get(key, None)

        try:
            default_index = options.index(vorhandene_auswahl) if vorhandene_auswahl in options else 0
        except ValueError:
            default_index = 0

        # Zeige Radio an – OHNE key (sonst wird State doppelt geführt)
        auswahl = st.radio(frage, options, index=default_index, key=f"{key}_temp")

        # Speichere Auswahl explizit in Session State
        st.session_state[key] = auswahl
        st.session_state[f"{key}_score"] = categorize_func(auswahl)

    radio_with_categorization(
        "Wie viele CNC-Werkzeugmaschinen haben Sie in Ihrer zerspanenden Fertigung?",
        ["< 5", "5-10", "11-24", "≥ 25"],
        "cnc_range",
        categorize_cnc_machines
    )

    radio_with_categorization(
        "Wie viel Prozent Ihrer CNC-Werkzeugmaschinen besitzen eine Automation für den Werkstückwechsel?",
        ["0%", "1-25%", "26-49%", "≥ 50%"],
        "automation_range",
        categorize_automation_percentage
    )

    radio_with_categorization(
        "Welche durchschnittlichen Losgrößen werden bei Ihnen gefertigt?",
        ["< 5", "5-50", "51-99", "≥ 100"],
        "losgroesse_range",
        categorize_losgroesse
    )

    radio_with_categorization(
        "Wie lang ist die durchschnittliche Durchlaufzeit (von Rohmaterial bis zum unentgrateten Fertigteil)?",
        ["< 10 min", "11–30 min", "31–89 min", "≥ 90 min"],
        "durchlaufzeit_range",
        categorize_durchlaufzeit
    )

    radio_with_categorization(
        "Welche durchschnittliche Laufzeit haben die Werkstücke?",
        ["< 1 Tag", "1–3 Tage", "4–6 Tage", "≥ 7 Tage"],
        "laufzeit_range",
        categorize_laufzeit
    )

    st.subheader("Personen- und unternehmensbezogene Angaben")
    st.radio("In welcher Funktion sind Sie tätig?",
        ["Geschäftsführer", "Produktions-/ Fertigungsleitung", "Arbeitsvorbereitung", "Teamleitung", "Planungsabteilung (IE, Lean etc.)", "Weitere"],
        key="funktion_radio_input")

    st.radio("Wie viele Mitarbeitende arbeiten in Ihrem Unternehmen?",
        ["1-9", "10-49", "50-199", "200-499", "500-1999", "≥2000"],
        key="mitarbeitende_radio_input")

    st.text_input("Für welche Branche fertigen Sie?", key="branche_input")
    st.text_input("PLZ (optional)", key="plz_input")
    st.text_input("E-Mail (optional)", key="email_input")

    st.info("Vielen Dank. Sie können nun zur Auswertung übergehen.")
    
# Inhalt Auswertungs-Tab

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

            # Reihenfolge für MTOK-Struktur (Uhrzeigersinn)
            labels_ordered = [
                "Produktivität und Motivation (Mensch)",
                "Persönliches Umfeld (Mensch)",
                "Arbeitsplatzgestaltung und Automatisierung (Technik)",
                "IT-Systemlandschaft und digital vernetzte Infrastruktur (Technik)",
                "Kommunikation, Kooperation und Zusammenarbeit (Organisation)",
                "Organisatorische Umwelt (Organisation)",
                "Produktionsorganisation (Organisation)",
                "Unternehmenskultur (Kultur)",
                "Soziale Beziehungen und Interaktion (Kultur)"
            ]

            # Werte entsprechend sortieren (achte auf die korrekte Reihenfolge)
            values_ordered = [
                st.session_state.ergebnisse.get("Produktivität und Motivation", 1),
                st.session_state.ergebnisse.get("Persönliches Umfeld", 1),
                st.session_state.ergebnisse.get("Arbeitsplatzgestaltung und Automatisierung", 1),
                st.session_state.ergebnisse.get("IT-Systemlandschaft und digital vernetzte Infrastruktur", 1),
                st.session_state.ergebnisse.get("Kommunikation, Kooperation und Zusammenarbeit", 1),
                st.session_state.ergebnisse.get("Organisatorische Umwelt", 1),
                st.session_state.ergebnisse.get("Produktionsorganisation", 1),
                st.session_state.ergebnisse.get("Unternehmenskultur", 1),
                st.session_state.ergebnisse.get("Soziale Beziehungen und Interaktion", 1)
            ]
    
            # Winkel und Werte zyklisch schließen
            angles = np.linspace(0, 2 * np.pi, len(labels_ordered), endpoint=False).tolist()
            values_cycle = values_ordered + values_ordered[:1]
            angles_cycle = angles + angles[:1]

            # Labels umbrechen für bessere Lesbarkeit
            wrapped_labels = [label.replace(" und ", "\nund ").replace("(", "\n(") for label in labels_ordered]
        
            # Plot erzeugen
            fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))
            ax.set_theta_offset(np.pi / 2)      # Start bei 12 Uhr
            ax.set_theta_direction(-1)           # Uhrzeigersinn

            ax.plot(angles_cycle, values_cycle, color='royalblue', linewidth=2)
            ax.fill(angles_cycle, values_cycle, color='cornflowerblue', alpha=0.25)

            ax.set_xticks(angles)
            ax.set_xticklabels(wrapped_labels, fontsize=7)

            ax.set_yticks([1, 2, 3, 4])
            ax.set_yticklabels(['1', '2', '3', '4'], fontsize=7, color='gray')
            ax.set_ylim(0, 4)

            ax.yaxis.grid(True, linestyle='dotted', color='lightgray')
            ax.xaxis.grid(True, linestyle='solid', color='lightgray')
            ax.set_title("Cluster-Profil", fontsize=14, pad=20)

            # Ausgabe in Streamlit
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
            buf.seek(0)
            st.image(buf, width=700)
    
        else:
            st.warning("❗ Keine gültigen Werte für Radar-Diagramm vorhanden.")
          

        # Cluster-Zuordnung
        cluster_result, abweichungen_detail = berechne_clusterzuordnung(Kriterien)
        display_cluster_result = cluster_result
        st.session_state["cluster_result"] = cluster_result
        st.session_state["abweichungen_detail"] = abweichungen_detail

        if isinstance(cluster_result, str) and "Bitte bewerten Sie" in cluster_result:
            st.warning(cluster_result)
        else:
            st.subheader("Automatische Clusterzuordnung")
            st.success(f"Der Betrieb wird dem folgenden Cluster zugeordnet:\n\n**{cluster_result}**")

            # Clusterbeschreibung
            st.subheader("Clusterbeschreibung")
            cluster_beschreibungen = {
                "Cluster 1 – Traditionell und reaktiv": (
                    "Dieses Cluster ist geprägt durch eine geringe Technikaffinität, hohe Prozessunsicherheit und eine niedrige Offenheit "
                    "für neue Arbeitsformen. Digitale Systeme sind häufig veraltet oder nur punktuell vorhanden. Mobile oder zeitflexible "
                    "Arbeitsmodelle werden nicht genutzt oder aktiv abgelehnt. Die Führung agiert überwiegend hierarchisch, Veränderungsbereitschaft "
                    "ist kaum erkennbar. Die Einführung flexibler Arbeit erfordert grundlegende strukturelle, kulturelle und technische Vorarbeiten."
                ),
                "Cluster 2 – Produktionsstark, aber mobilitätsfern": (
                    "Betriebe dieses Clusters verfügen über eine moderne technische Ausstattung und stabile Produktionsprozesse, "
                    "zeigen jedoch eine geringe Offenheit und Akzeptanz für mobile oder flexible Arbeitsformen. Die Wertschöpfung im Produktionsbereich "
                    "steht klar im Vordergrund. Kulturelle Barrieren sowie fehlende organisatorische Modelle zur Flexibilisierung hemmen den Wandel. "
                    "Technisch wäre Flexibilität oft bereits möglich, scheitert jedoch an Einstellung, Struktur oder fehlender Systematik."
                ),
                "Cluster 3 – Digital-affin und akzeptanzstark": (
                    "Diese Unternehmen zeichnen sich durch eine hohe Technikreife, stabile Prozesse sowie eine starke Offenheit für neue Arbeitsformen aus. "
                    "Mobile und zeitflexible Arbeit wird bereits eingesetzt oder ist in Pilotbereichen etabliert. Die Führungskultur ist dialogorientiert, "
                    "und Beschäftigte werden aktiv eingebunden. Dieses Cluster hat sehr gute Voraussetzungen, flexible Arbeit systematisch auszurollen "
                    "und weiterzuentwickeln – sowohl technisch als auch kulturell-organisatorisch."
                ),
                "Cluster 4 – Technisch solide, aber prozessual träge": (
                    "In diesem Cluster sind zwar solide technische Grundlagen vorhanden (z. B. ERP, CAD, IT-Support), doch lange Laufzeiten, hohe Komplexität "
                    "und eine geringe Umsetzungsgeschwindigkeit behindern die Einführung flexibler Arbeit. Veränderungsprozesse laufen schleppend. "
                    "Die Belegschaft ist nicht grundsätzlich ablehnend, doch es fehlt an konkreten Umsetzungsstrategien und an kommunikativer Begleitung. "
                    "Technik und Akzeptanz bilden eine gute Basis – der Fokus muss auf Prozessvereinfachung und klarer Umsetzung liegen."
                )
            }
            st.info(cluster_beschreibungen.get(cluster_result, "Keine Beschreibung verfügbar."))


 
            # Handlungsempfehlungen nach Cluster und MTOK
            st.subheader("Clusterspezifische Handlungsempfehlungen")
            handlungsempfehlungen = {
            "Cluster 1 – Traditionell und reaktiv": {
                "Technik": [
                    "- Prüfen Sie grundlegende digitale Infrastruktur (z. B. WLAN in Büros und Besprechungsräumen).",
                    "- Beginnen Sie mit einfach implementierbaren Tools (z. B. digitale Schichtpläne oder Messenger)."
                ],
                "Organisation": [
                    "- Entwickeln Sie Pilotmodelle für Zeitflexibilität (z. B. Gleitzeit in indirekten Bereichen).",
                    "- Führen Sie standardisierte Feedbackprozesse ein, um Veränderungsresistenz zu adressieren."
                ],
                "Kultur": [
                    "- Starten Sie mit Führungskräfte-Coachings zur Gestaltung flexibler Arbeit.",
                    "- Etablieren Sie eine positive Fehler- und Lernkultur durch regelmäßige Teambesprechungen."
                ],
                "Mensch": [
                    "- Sensibilisieren Sie Mitarbeitende für den Nutzen flexibler Arbeit (z. B. Workshops, Aushänge).",
                    "- Unterstützen Sie betroffene Beschäftigte durch kurze Schulungsmaßnahmen zur Selbstorganisation."
                ]
            },
            "Cluster 2 – Produktionsstark, aber mobilitätsfern": {
                "Technik": [
                    "- Binden Sie Produktionsdaten gezielt in Dashboard-Lösungen ein (z. B. Power BI).",
                    "- Stellen Sie Remote-Zugriffe für Planer:innen und AV-Bereiche bereit (z. B. VPN, TDM-Clients)."
                ],
                "Organisation": [
                    "- Entwickeln Sie Teilzeit- und Schichtmodelle mit Fokus auf bestimmte Berufsgruppen.",
                    "- Schaffen Sie Transparenz über Aufgaben, die auch remote bearbeitbar sind."
                ],
                "Kultur": [
                    "- Thematisieren Sie Mobilitätsoptionen in Führungsrunden offen und lösungsorientiert.",
                    "- Heben Sie die Vereinbarkeit von Familie und Beruf in internen Leitbildern stärker hervor."
                ],
                "Mensch": [
                    "- Befähigen Sie Fachkräfte in AV, Konstruktion oder QS gezielt zur Nutzung flexibler Tools.",
                    "- Nutzen Sie Erfahrungsberichte von Pilotbereichen als Impuls für weitere Mitarbeitende."
                ]
            },
            "Cluster 3 – Digital-affin und akzeptanzstark": {
                "Technik": [
                    "- Prüfen Sie fortgeschrittene Tools zur kollaborativen Zusammenarbeit (z. B. MS Teams mit Planner).",
                    "- Nutzen Sie digitale Schichtplanungs- oder Urlaubsantragssysteme zur weiteren Flexibilisierung."
                ],
                "Organisation": [
                    "- Etablieren Sie feste Review-Zyklen zur Bewertung und Weiterentwicklung flexibler Arbeit.",
                    "- Schaffen Sie klare Regeln zur Erreichbarkeit und Aufgabentransparenz im mobilen Arbeiten."
                ],
                "Kultur": [
                    "- Verstärken Sie Wertschätzung durch autonome Arbeitsgestaltung und Entscheidungsspielräume.",
                    "- Fördern Sie teaminterne Aushandlungsprozesse über Präsenz- und Mobilezeiten."
                ],
                "Mensch": [
                    "- Nutzen Sie das Potenzial erfahrener Mitarbeitender für Mentoring im Umgang mit Flexibilität.",
                    "- Stärken Sie Selbstlernkompetenzen durch E-Learning-Angebote oder Selbstcoaching-Inhalte."
                ]
            },
            "Cluster 4 – Technisch solide, aber prozessual träge": {
                "Technik": [
                    "- Identifizieren Sie technische Engpässe in der Datenverfügbarkeit (z. B. Live-Kennzahlenanzeige).",
                    "- Setzen Sie auf Assistenzsysteme, die Mobilität auch in getakteten Bereichen ermöglichen."
                ],
                "Organisation": [
                    "- Reduzieren Sie Durchlaufzeiten und Komplexität in ausgewählten Kernprozessen.",
                    "- Entwickeln Sie Umsetzungsroadmaps für Pilotbereiche mit klaren Meilensteinen."
                ],
                "Kultur": [
                    "- Reduzieren Sie Umsetzungsbarrieren durch interne Kommunikation mit Best-Practice-Beispielen.",
                    "- Integrieren Sie betriebliche Interessenvertretungen frühzeitig in Transformationsvorhaben."
                ],
                "Mensch": [
                    "- Schaffen Sie Sicherheit durch klare Rollendefinitionen und transparente Arbeitsaufträge.",
                    "- Fördern Sie aktive Beteiligung z. B. durch Befragungen und Change-Botschafter:innen."
                ]
            }
        }
            
            cluster_empfehlungen = handlungsempfehlungen.get(cluster_result, {})

            # 1. Darstellung in App
            for dimension in ["Technik", "Organisation", "Kultur", "Mensch"]:
                if dimension in cluster_empfehlungen:
                    st.markdown(f"### {dimension}")
                    for empfehlung in cluster_empfehlungen[dimension]:
                        st.markdown(f"- {empfehlung}")
                    st.markdown("---")
            
            cluster_beschreibung_html = f"""
            <h2>Clusterbeschreibung</h2>
            <div class="box">
                {cluster_beschreibungen.get(cluster_result, "Keine Beschreibung verfügbar.")}
            </div>
            """

            empfehlungen_html = ""
            for dimension in ["Technik", "Organisation", "Kultur", "Mensch"]:
                if dimension in cluster_empfehlungen:
                    empfehlungs_block = "<ul>"  # Hier beginnt die Liste!
                    for empfehlung in cluster_empfehlungen[dimension]:
                        empfehlungs_block += f"<li>{empfehlung[2:]}</li>"  # Entferne führendes "- "
                    empfehlungs_block += "</ul>"
                    empfehlungen_html += f"<h3>{dimension}</h3>{empfehlungs_block}"
        
            # Tabelle erzeugen
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

            # HTML-Komplettausgabe
            html_content = f"""
            <!DOCTYPE html>
            <html lang=\"de\">
            <head>
                <meta charset=\"utf-8\">
                <title>Standortbestimmung</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: auto; line-height: 1.6; }}
                    h1 {{ font-size: 26px; color: #003366; }}
                    h2 {{ font-size: 20px; color: #005599; margin-top: 30px; }}
                    h3 {{ font-size: 16px; color: #333333; margin-top: 20px; }}
                    .box {{ background: #f8f9fa; padding: 15px; border-left: 5px solid #005599; border-radius: 5px; margin-bottom: 25px; }}
                    img {{ display: block; margin: 20px auto; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ccc; padding: 8px; font-size: 13px; }}
                    th {{ background-color: #e1e9f0; text-align: left; }}
                    td:nth-child(3) {{ text-align: center; }}
                    ul {{ margin-top: 0; }}
                    li {{ margin-bottom: 6px; }}
                </style>
            </head>
            <body>
                <h1>Ergebnisse des Modells</h1>
                <div class=\"box\"><strong>Clusterzuordnung:</strong><br>{display_cluster_result}</div>
                {cluster_beschreibung_html}
                <h2>Clusterspezifische Handlungsempfehlungen</h2>
                {empfehlungen_html}
                <h2>Cluster-Profil</h2>
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
            
if current_tab == "Evaluation":

    # Einführungstext
    st.markdown("""
        <div style='font-size: 1.1rem; margin-bottom: 1rem;'>
            Vielen Dank für die Bearbeitung des entwickelten Modells.  
            Um die Qualität weiter zu verbessern, bitten wir Sie um eine kurze Bewertung.
        </div>
    """, unsafe_allow_html=True)

    # Bewertungsoptionen
    options = ["Niedrig", "Mittel", "Hoch", "Sehr hoch"]

    # Hilfsfunktion zur sicheren Umwandlung von Werten (mit Platzhalter für leere Werte)
    def safe_value(val):
        try:
            if val in [None, ""] or (isinstance(val, float) and np.isnan(val)):
                return "99999"
            return str(val)
        except Exception:
            return "99999"

    # Funktion zur Anzeige einer Frage (wie bei den Handlungsfeldern)
    def zeige_fragen(titel, fragen_liste, prefix):
        st.subheader(titel)
        for idx, frage in enumerate(fragen_liste):
            radio_key = f"{prefix}_{idx}"

            st.markdown(f"""
                <div style='margin-bottom: -0.2rem; margin-top: 0.7rem'>
                    <strong>{frage}</strong>
                </div>
            """, unsafe_allow_html=True)

            score = st.radio(
                label="",
                options=options,
                key=radio_key,
                index=0
            )

            st.session_state[radio_key + "_score"] = score

    # Bereich 1 – Verständlichkeit
    fragen_1 = [
        "Die Struktur des Modells war für mich durchgängig nachvollziehbar.",
        "Die verwendeten Begriffe und Formulierungen in den Bewertungskriterien waren klar verständlich.",
        "Die Erklärungen zu Handlungsfeldern und Bewertungsskalen waren verständlich und hilfreich.",
        "Die Clusterzuordnung war für mich nachvollziehbar.",
        "Die grafische Darstellung der Ergebnisse war verständlich."
    ]
    zeige_fragen("1. Verständlichkeit und Transparenz des Modells", fragen_1, "eval1")

    # Bereich 2 – Relevanz
    fragen_2 = [
        "Die im Modell adressierten Themenfelder sind für unser Unternehmen relevant.",
        "Die Bewertungskriterien spiegeln praxisrelevante Herausforderungen in der Produktion wider.",
        "Die im Modell hinterlegten Handlungsempfehlungen lassen sich auf unseren betrieblichen Alltag übertragen.",
        "Die Clusterprofile bilden typische Ausgangslagen in der industriellen Produktion realistisch ab.",
        "Die Branchenspezifika der zerspanenden Fertigung wurden im Modell angemessen berücksichtigt."
    ]
    zeige_fragen("2. Relevanz und betriebliche Passung", fragen_2, "eval2")

    # Bereich 3 – Anwendbarkeit
    fragen_3 = [
        "Das Modell eignet sich als Instrument zur Systematisierung flexibler Arbeit.",
        "Mit Hilfe des Modells lassen sich konkrete betriebliche Entwicklungsmaßnahmen ableiten.",
        "Die Umsetzung als digitales Tool war funktional und benutzerfreundlich.",
        "Das Modell unterstützt eine strukturierte Selbstbewertung und Reflexion im Unternehmen."
    ]
    zeige_fragen("3. Anwendbarkeit und betrieblicher Nutzen", fragen_3, "eval3")

    # Bereich 4 – Tiefe
    fragen_4 = [
        "Das Modell berücksichtigt die zentralen Erfolgsfaktoren flexibler Arbeit systematisch.",
        "Die inhaltliche Tiefe und Differenzierung der Bewertungskriterien war angemessen."
    ]
    zeige_fragen("4. Vollständigkeit und konzeptionelle Tiefe", fragen_4, "eval4")

    # Bereich 5 – Gesamturteil
    fragen_5 = [
        "Das Modell ist insgesamt logisch aufgebaut und stimmig konzipiert.",
        "Ich würde das Modell anderen Unternehmen oder Kolleg:innen weiterempfehlen.",
        "Der erwartete Nutzen des Modells überwiegt den Aufwand der Anwendung."
    ]
    zeige_fragen("5. Gesamturteil und Weiterempfehlung", fragen_5, "eval5")

    # Bereich 6 – Freitext
    st.subheader("6. Offene Rückmeldung")
    st.text_area(
        "Haben Sie Anregungen, Verbesserungsvorschläge oder Kritik zum Modell?",
        key="evaluation_feedback_text"
    )

    # Hilfsfunktion zur Bewertungskonvertierung
    def bewertung_in_zahl(wert):
        mapping = {
            "Niedrig": 1,
            "Mittel": 2,
            "Hoch": 3,
            "Sehr hoch": 4
        }
        return mapping.get(wert, 99999)

    # Hilfsfunktion zur sicheren Speicherung
    def safe_value(val):
        if val is None:
            return 99999
        if isinstance(val, float) and np.isnan(val):
            return 99999
        if isinstance(val, str):
            if val.strip() == "":
                return 99999
            return val  # Freitext oder Cluster-Text erhalten
        return val

      # Anzahl bewerteter MTOK-Felder zählen
    def zaehle_bewertete_clustervariablen(mtok_daten):
        werte = list(mtok_daten.values())[:9]  # Nur die 9 MTOK-Felder
        return sum(1 for v in werte if isinstance(v, (int, float)) and v > 0)


    # Absenden und speichern
    if st.button("Absenden und speichern"):
        evaluation_data = {}
    
        # 1. Evaluation speichern
        for i in range(1, 6):
            fragen_count = len(eval(f"fragen_{i}"))
            for j in range(fragen_count):
                key = f"eval{i}_{j}"
                antwort = st.session_state.get(f"{key}_score", "")
                zahlwert = bewertung_in_zahl(antwort)
                evaluation_data[key] = safe_value(zahlwert)

        # 2. Freitextfeld
        evaluation_data["feedback"] = st.session_state.get("evaluation_feedback_text", "")

        # 3. MTOK-Werte auslesen 
        mtok_keys = [
            "Produktivität und Motivation",
            "Persönliches Umfeld",
            "Arbeitsplatzgestaltung und Automatisierung",
            "IT-Systemlandschaft und digital vernetzte Infrastruktur",
            "Kommunikation, Kooperation und Zusammenarbeit",
            "Organisatorische Umwelt",
            "Produktionsorganisation",
            "Unternehmenskultur",
            "Soziale Beziehungen und Interaktion"
        ]

        mtok_raw = st.session_state.get("ergebnisse", {})
        mtok_werte = {}

        for key in mtok_keys:
            val = mtok_raw.get(key, 99999)
            if isinstance(val, (int, float)):
                mtok_werte[key] = float(val)
            else:
                mtok_werte[key] = 99999.0  # wenn leer, Text, None etc.

        # 4. Cluster-Zuordnung (aus Session State laden, nicht neu berechnen)
        cluster_result = st.session_state.get("cluster_result", None)
        abweichungen_detail = st.session_state.get("abweichungen_detail", {})

        # Anzahl bewerteter MTOK-Felder zählen
        bewertete = zaehle_bewertete_clustervariablen(mtok_werte)

        # Bewertung und Cluster-Scores nur übernehmen, wenn valide
        if isinstance(cluster_result, str) and isinstance(abweichungen_detail, dict) and bewertete >= 7:
            cluster_scores = {
                "Zugeordnetes Cluster": cluster_result,
                **{f"Abweichung {k}": v for k, v in abweichungen_detail.items()}
            }
        else:
            cluster_scores = {
                "Zugeordnetes Cluster": f"Bitte bewerten Sie mindestens 7 relevante Kriterien-Sets (Cluster-Variablen) für eine präzise Clusterzuordnung. Aktuell sind {bewertete} bewertet.",
                "Abweichung 1": 99999,
                "Abweichung 2": 99999,
                "Abweichung 3": 99999,
                "Abweichung 4": 99999
            }

        daten_gesamt = {}
        daten_gesamt.update(mtok_werte)
        daten_gesamt.update(cluster_scores)
        daten_gesamt.update(evaluation_data)
        daten_gesamt["Zeitstempel"] = datetime.now().isoformat()

        # Speichern in Google Sheet
        try:
            daten_liste = [safe_value(v) for v in daten_gesamt.values()]
            worksheet.append_row(daten_liste)
            st.success("Vielen Dank! Ihre Rückmeldung wurde gespeichert.")
        except Exception as e:
            st.error(f"Fehler beim Speichern: {e}")
            
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
