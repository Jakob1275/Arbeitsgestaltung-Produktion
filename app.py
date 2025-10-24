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
import html

#Google Sheet Verbindung

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

#Titel der Seiten
st.set_page_config(page_title="Modell zur Systematisierung flexibler Arbeit", layout="wide")

# Style-Block
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-size: 18px !important;
        line-height: 1.6;
    }

    div[data-baseweb="radio"] {
        margin-bottom: -10px !important;
    }

    .evaluation-section {
        margin-bottom: 2.2rem;
    }

    .evaluation-question {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 0.2rem;
        color: #222;
    }
 
    .evaluation-block {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
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
        margin-bottom: 0.2rem;
    }

    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        border-bottom: 1px solid #ddd;
        border-radius: 0px;
    }

    .header-title {
        flex-grow: 1;
    }

    .logo-container {
        display: flex;
        gap: 1rem;
        align-items: center;
        border-radius: 0px;
    }

    .logo-container img {
        max-height: 50px;
        height: auto;
        width: auto;
        border-radius: 0px;
    }

    .text-box {
        padding: 1.2rem;
        background-color: #f0f0f0;
        border-left: 5px solid #0066cc;
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        font-size: 17px;
        line-height: 1.6;
    }

    img {
    border-radius: 0px !important;
    box-shadow: none !important;
    }

    div[data-baseweb="radio"] {
    margin-left: 1rem;
    }
    
</style>
""", unsafe_allow_html=True)

# Header mit Logos
col1, col2, col3 = st.columns([5, 1, 1])

with col1:
    st.markdown("## Modell zur Systematisierung flexibler Arbeit")
    st.markdown("*Typisierung und Gestaltung mobiler und zeitflexibler Arbeit in der zerspanenden Fertigung*")

with col2:
    st.image("kit-logo-en.svg", width=120)

with col3:
    st.image("FH-Logo.png", width=180)

# MTOK-Dimensionen und Handlungsfelder
mtok_structure = {
    "Mensch": ["Qualifikation und Kompetenzentwicklung", "Persönliche Voraussetzungen"],
    "Technik": ["Automatisierung und Arbeitsplatzgestaltung", "Digitale Vernetzung und IT-Infrastruktur"],
    "Organisation": ["Kommunikation, Kooperation und Zusammenarbeit", "Organisatorische Umwelt", "Produktionsorganisation"],
    "Kultur": ["Unternehmenskultur", "Führung und Teamzusammenhalt"]
}

einleitungstexte = {
    "Qualifikation und Kompetenzentwicklung": (
        "Die folgenden Aussagen beziehen sich auf betriebliche Maßnahmen zur Schulung, "
        "Qualifizierung und Kompetenzentwicklung für flexible Arbeit in der zerspanenden Fertigung."
    ),
    "Persönliche Voraussetzungen": (
        "Die folgenden Aussagen beziehen sich auf persönliche Einstellungen, Haltungen, Fähigkeiten und "
        "die individuelle Bereitschaft der Beschäftigten, mobile, zeitflexible und digital unterstützte "
        "Arbeit in der zerspanenden Fertigung umzusetzen."
    ),
    "Automatisierung und Arbeitsplatzgestaltung": (
        "Die folgenden Aussagen beziehen sich auf Automatisierung, ergonomische Gestaltung "
        "und die physische Arbeitsumgebung in der Fertigung."
    ),
    "Digitale Vernetzung und IT-Infrastruktur": (
        "Die folgenden Aussagen beziehen sich auf digitale Systeme, Datenflüsse und technische Infrastruktur, "
        "die eine orts- und zeitflexible Arbeit in der Fertigung ermöglichen."
    ),
    "Kommunikation, Kooperation und Zusammenarbeit": (
        "Die folgenden Aussagen beziehen sich auf betriebliche Strukturen und Instrumente, "
        "die eine wirksame Kommunikation und Zusammenarbeit über Arbeitsorte und Zeiten hinweg fördern."
    ),
    "Organisatorische Umwelt": (
        "Die folgenden Aussagen beziehen sich auf betriebliche und rechtliche Rahmenbedingungen, "
        "die die Umsetzung flexibler Arbeitsformen in der zerspanenden Fertigung beeinflussen."
    ),
    "Produktionsorganisation": (
         "Die folgenden Aussagen beziehen sich auf Abläufe, Planungslogiken und organisatorische Strukturen, "
        "die eine effiziente und zugleich flexible Produktionsgestaltung unterstützen."
    ),
    "Unternehmenskultur": (
        "Die folgenden Aussagen beziehen sich auf grundlegende Einstellungen, Werte und kulturelle Prinzipien, "
        "die den Umgang mit flexibler Arbeit im Unternehmen prägen."
    ),
    "Führung und Teamzusammenhalt": (
        "Die folgenden Aussagen beziehen sich auf Führungsverhalten und soziale Dynamiken im Team, "
        "die Vertrauen, Selbstverantwortung und Zusammenhalt in flexiblen Arbeitsumgebungen fördern."
    ),
}

# Kriterienliste
Kriterien = {
"Qualifikation und Kompetenzentwicklung": [
  {
    "frage": "M1.1 Anforderungen an mobile Arbeit werden systematisch vermittelt (z. B. durch Schulungen oder Leitfäden).",
    "begründung": "Mobile Arbeit setzt unter anderem einen sicheren IT-Zugang, die Einbindung in digitale Prozesse und eigenverantwortliches Arbeiten voraus."
  },
  {
    "frage": "M1.2 Voraussetzungen und Grenzen zeitflexibler Arbeit werden klar kommuniziert.",
    "begründung": "Nur wenn die Voraussetzungen und Grenzen zeitflexibler Arbeit bekannt sind, kann diese in der Zerspanung realistisch und störungsfrei umgesetzt werden."
  },
  {
    "frage": "M1.3 Beschäftigte erhalten gezielte Unterstützung, um bei Prozessabweichungen eigenverantwortlich und sicher zu handeln.",
    "begründung": "In flexiblen Arbeitsmodellen ist es entscheidend, dass Beschäftigte auch ohne direkte Aufsicht Störungen erkennen und beheben können."
  },
  {
    "frage": "M1.4 Die betriebliche Kompetenzentwicklung fördert gezielt die Selbstorganisation und Entscheidungsfähigkeit im Rahmen flexibler Arbeit.",
    "begründung": "Selbstorganisiertes Arbeiten erfordert kontinuierliche Weiterentwicklung."
  }
  ],
  "Persönliche Voraussetzungen": [
    {
      "frage": "M2.1 Beschäftigte zeigen Offenheit gegenüber mobiler Arbeit.",
      "begründung": "Eine positive Grundhaltung erleichtert den Einstieg in ortsunabhängiges Arbeiten und unterstützt die Akzeptanz neuer Arbeitsformen."
    },
    {
      "frage": "M2.2 Beschäftigte zeigen Offenheit gegenüber zeitflexibler Arbeit.",
      "begründung": "Offenheit gegenüber flexiblen Arbeitszeiten fördert Anpassungsfähigkeit und Akzeptanz betrieblicher Veränderungen."
    },
    {
      "frage": "M2.3 Beschäftigte verfügen über die Fähigkeit, ihre Arbeit eigenständig zu strukturieren und zu organisieren.",
      "begründung": "Selbstorganisation ist eine zentrale Voraussetzung, um mobil oder zeitflexibel effizient und verantwortungsvoll arbeiten zu können."
    },
    {
      "frage": "M2.4 Beschäftigte bringen regelmäßig eigene Ideen und Verbesserungsvorschläge ein.",
      "begründung": "Eigeninitiative und Mitgestaltung fördern Motivation und die Weiterentwicklung betrieblicher Flexibilisierungskonzepte."
    },
    {
      "frage": "M2.5 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren wesentlichen Funktionen.",
      "begründung": "Systemverständnis erhöht Handlungssicherheit, reduziert Fehlbedienungen und unterstützt die Integration digitaler Technologien in den Arbeitsalltag."
    },
    {
      "frage": "M2.6 Beschäftigte stehen neuen, digital vernetzten Technologien und Abläufen offen und veränderungsbereit gegenüber.",
      "begründung": "Technikakzeptanz und Veränderungsbereitschaft sind zentrale Voraussetzungen für den erfolgreichen Umgang mit digitalisierten Arbeitsprozessen."
    }
    ],
   "Automatisierung und Arbeitsplatzgestaltung": [
    {
        "frage": "T1.1 Zerpanende Fertigungsprozesse sind störungsarm.",
        "begründung": "Stabile Prozesse reduzieren Eingriffe und schaffen Grundlagen für flexible Arbeitsmodelle."
    },
    {
        "frage": "T1.2 Werkzeugmaschinen können über längere Zeiträume ohne ständige Anwesenheit betrieben werden.",
        "begründung": "Ein hoher Automatisierungsgrad oder lange unbeaufsichtigte Laufzeiten ermöglichen zeitliche Entkopplung und reduzieren Präsenzzwänge."
    },
    {
        "frage": "T1.3 Am oder nahe dem Maschinenarbeitsplatz sind Bereiche für computergestützte Tätigkeiten und digitale Zusammenarbeit vorhanden.",
        "begründung": "Bereiche an der Maschine oder getrennte Räumlichkeiten ermöglichen Tätigkeiten wie Videokonferenzen, Planung oder Dokumentation in Fertigungsnähe."
    },
    {
        "frage": "T1.4 Fertigungsprozesse sind standardisiert dokumentiert.",
        "begründung": "Standardisierung erleichtert Vertretungen, Übergaben und mobile Unterstützungsformate."
    },
    {
        "frage": "T1.5 Die ergonomische Gestaltung der Arbeitsplätze unterstützt eine gesundheitsförderliche Arbeit.",
        "begründung": "Ergonomische Arbeitsplätze reduzieren physische Belastung und fördern Leistungsfähigkeit bei flexiblen Arbeitszeiten."
    },
   ],
   "Digitale Vernetzung und IT-Infrastruktur": [
    {
        "frage": "T2.1 Mobile Endgeräte stehen für mobile Arbeit zur Verfügung.",
        "begründung": "Mobile Endgeräte wie Laptops oder Tablets sind Grundvoraussetzung für ortsunabhängiges Arbeiten.",
        "einschraenkung": "1_und_4"
    },
    {
        "frage": "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich.",
        "begründung": "Sichere Verbindungen, etwa über VPN, ermöglichen flexibles Arbeiten außerhalb der Fertigung.",
        "einschraenkung": "1_und_4"
    },
    {
        "frage": "T2.3 Prozess- und Maschinendaten stehen in Echtzeit digital zur Verfügung.",
        "begründung": "Echtzeitdaten ermöglichen Steuerung und Optimierung auch bei variabler Anwesenheit."
    },
    {
        "frage": "T2.4 Fernüberwachung und -zugriff auf Maschinen sind möglich.",
        "begründung": "Monitoring-Tools oder Kameras erlauben Eingriffe ohne dauerhafte Präsenz."
    },
    {
        "frage": "T2.5 Werkzeuge und Betriebsmittel sind digital erfasst und jederzeit verfügbar.",
        "begründung": "Digitale Toolmanagement-Systeme ermöglichen eine flexible und effiziente Betriebsmittelplanung."
    },   
    {
        "frage": "T2.6 Der IT-Support kann auch produktionsbezogene IT-Probleme beheben.",
        "begründung": "Zuverlässiger IT-Support sichert technische Funktionsfähigkeit und reduziert Akzeptanzbarrieren.",
        "einschraenkung": "1_und_4"
    },
    {
        "frage": "T2.7 IT-Sicherheitskonzepte sind etabliert und werden regelmäßig geprüft.",
        "begründung": "Starke IT-Sicherheit schützt sensible Daten und gewährleistet stabile Abläufe bei flexibler Arbeit.",
        "einschraenkung": "1_und_4"
    }
    ],
    "Kommunikation, Kooperation und Zusammenarbeit": [
    {
      "frage": "O1.1 Informationen zu Planung, Schichtübergaben und Störfällen sind digital und zeitnah verfügbar.",
      "begründung": "Ein verlässlicher Informationsfluss ermöglicht schnelle Reaktionen und koordinierte Abläufe bei flexibler Arbeit."
    },
    {
      "frage": "O1.2 Erfahrungswissen wird dokumentiert und digital zugänglich gemacht.",
      "begründung": "Systematischer Wissenstransfer fördert Qualität, Lernen und Unabhängigkeit von Einzelpersonen."
    },
    {
      "frage": "O1.3 Verantwortlichkeiten sind klar geregelt und relevante Akteure (z. B. Betriebsrat, Datenschutz) eingebunden.",
      "begründung": "Klare Rollen und Beteiligung schaffen Transparenz, Rechtssicherheit und Vertrauen."
    },
    {
      "frage": "O1.4 Erwartungen an dauerhafte Erreichbarkeit sind klar geregelt und werden begrenzt.",
      "begründung": "Klare Grenzen fördern Erholung, Selbststeuerung und nachhaltige Nutzung flexibler Arbeitsmodelle."
    }
    ],
    "Organisatorische Umwelt": [
    {
      "frage": "O2.1 Rechtliche Vorgaben zu flexibler Arbeit sind bekannt und werden eingehalten.",
      "begründung": "Rechtskonformität zu Arbeitszeit, Datenschutz und Arbeitsschutz stärkt Vertrauen und Akzeptanz flexibler Modelle.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.2 Verbindliche Betriebsvereinbarungen zu mobiler und zeitflexibler Arbeit bestehen.",
      "begründung": "Klare Regelungen schaffen Rechtssicherheit, Orientierung und Transparenz für Beschäftigte und Führungskräfte.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.3 Die Personalplanung berücksichtigt flexible Arbeitszeiten.",
      "begründung": "Digitale Planungssysteme wie MES oder ERP ermöglichen eine verlässliche Steuerung und Dokumentation flexibler Arbeitszeiten.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.4 Die Personalplanung berücksichtigt flexible Arbeitsorte.",
      "begründung": "Systemische Einbindung in Planungstools ermöglicht die Koordination ortsunabhängiger Einsätze.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "O2.5 Beschäftigte können Beginn und Ende ihrer Arbeitszeit innerhalb festgelegter Grenzen selbst bestimmen.",
      "begründung": "Mitgestaltungsmöglichkeiten fördern Eigenverantwortung und Akzeptanz flexibler Arbeitszeitmodelle."
    },
    {
      "frage": "O2.6 Pausenregelungen lassen zeitliche Flexibilität im Rahmen betrieblicher Vorgaben zu.",
      "begründung": "Flexible Pausen erhöhen Erholung, Selbstbestimmung und Konzentrationsfähigkeit."
    },
    {
      "frage": "O2.7 Arbeitszeitkonten oder vergleichbare Systeme werden aktiv genutzt.",
      "begründung": "Transparente Zeitkonten fördern Fairness und eine ausgewogene Nutzung flexibler Arbeitszeiten.",
      "einschraenkung": "1_und_4"  
    }
    ],
    "Produktionsorganisation": [
    {
      "frage": "O3.1 Aufgaben sind hinsichtlich ihrer Präsenzbindung analysiert und systematisch aufteilbar.",
      "begründung": "Die Trennung von präsenzpflichtigen und mobil bearbeitbaren Tätigkeiten ist Grundlage jeder flexiblen Arbeitsgestaltung."
    },
    {
      "frage": "O3.2 Beschäftigte können während der Maschinenlaufzeit digitale Aufgaben (z. B. Programmierung, Dokumentation, Datenpflege) durchführen.",
      "begründung": "Die Einbindung digitaler Tätigkeiten in laufende Produktionsprozesse erhöht Effizienz, fördert hybride Facharbeit und schafft Grundlagen für mobile Arbeitsgestaltung."
    },
    {
      "frage": "O3.3 Lauf- und Durchlaufzeiten sind planbar und stabil steuerbar.",
      "begründung": "Planbare Prozesszeiten schaffen Handlungssicherheit und ermöglichen eine verlässliche Integration flexibler Arbeitszeitmodelle."
    },
    {
      "frage": "O3.4 Qualitätssicherungsprozesse sind automatisisert im Fertigungsprozess möglich.",
      "begründung": "Automatisierte Prüfverfahren reduzieren Kontrollaufwände und erhöhen die zeitliche Flexibilität im Produktionsablauf."
    },
    {
      "frage": "O3.5 Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
      "begründung": "Digitale Systeme ermöglichen Echtzeitsteuerung und flexible Anpassung an sich ändernde Rahmenbedingungen."
    },
    {
      "frage": "O3.6 Produktivitäts- und Qualitätskennzahlen werden regelmäßig analysiert und für Verbesserungen genutzt.",
      "begründung": "Eine systematische Rückkopplung zwischen Flexibilisierung und Produktivitätskennzahlen ist erforderlich, um Effizienzgewinne oder Zielkonflikte zu erkennen."
    }
        
    ],
    "Unternehmenskultur": [
    {
      "frage": "K1.1 Vertrauen bildet die Grundlage der Zusammenarbeit.",
      "begründung": "Vertrauen ist zentral für mobile und zeitflexible Arbeit, da Kontrolle nicht über physische Präsenz erfolgt.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "K1.2 Beschäftigte erhalten Handlungsfreiräume zur Gestaltung ihrer Arbeit.",
      "begründung": "Handlungsspielräume fördern Motivation, Eigenverantwortung und Innovationsfähigkeit."
    },
    {
      "frage": "K1.3 Zielerreichung und Ergebnisse stehen vor physischer Anwesenheit.",
      "begründung": "Ergebnisorientierung statt Präsenzkultur stärkt Eigenverantwortung und Flexibilisierung.",
      "einschraenkung": "1_und_4"
    },
    {
      "frage": "K1.4 Herausforderungen und Zielkonflikte flexibler Arbeit werden offen angesprochen und reflektiert.",
      "begründung": "Transparente Diskussion stärkt Vertrauen, ermöglicht Anpassungen und vermeidet dysfunktionale Überlastung."
    }
    ],
   "Führung und Teamzusammenhalt": [
   {
      "frage": "K2.1 Die Unternehmensführung lebt flexible Arbeitsformen sichtbar vor und positioniert sich aktiv dazu.",
      "begründung": "Vorbildverhalten auf oberster Ebene schafft Legitimität und Orientierung für nachgelagerte Führungsebenen.",
      "einschraenkung": "1_und_4"
    },
     {
      "frage": "K2.2 Führungskräfte unterstützen flexible Arbeitsformen aktiv und führen ergebnisorientiert.",
      "begründung": "Vertrauen und Ergebnisorientierung statt Präsenzkontrolle fördern Eigenverantwortung und Motivation im Team."
    },
     {
      "frage": "K2.3 Die Teamkultur ist von gegenseitiger Unterstützung und Kooperation geprägt.",
      "begründung": "Soziale Unterstützung erhöht Resilienz und Zusammenhalt bei reduzierter physischer Präsenz."
    },
    {
      "frage": "K2.4 Der Teamzusammenhalt wird aktiv gefördert, auch bei räumlicher oder zeitlicher Distanz.",
      "begründung": "Gezielte Maßnahmen (z. B. Teamevents, regelmäßige Meetings) verhindern soziale Isolation und stärken Bindung."
    },
    {
      "frage": "K2.5 Konflikte im Team werden frühzeitig erkannt und konstruktiv gelöst.",
      "begründung": "Ein strukturierter Umgang mit Konflikten sichert Vertrauen und Stabilität flexibler Arbeitsmodelle."
    }
    ]
    }

#Clusterbeschreibung
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

#Clusterbilder
cluster_bilder = {
    "Cluster 1 – Traditionell und reaktiv": "Cluster 1.png",
    "Cluster 2 – Produktionsstark, aber mobilitätsfern": "Cluster 2.png",
    "Cluster 3 – Digital-affin und akzeptanzstark": "Cluster 3.png",
    "Cluster 4 – Technisch solide, aber prozessual träge": "Cluster 4.png"
 }

#Definition Handlungsempfehlungen
handlungsempfehlungen = {
    "Cluster 1 – Traditionell und reaktiv": {
        "Technik": [
            {
                "text": "Führen Sie eine systematische Standortanalyse der technischen Infrastruktur durch – mit Fokus auf produktionsnahe IT-Grundversorgung (z. B. stabile Netzabdeckung, Arbeitsplatz-PCs, Zugang zu ERP/MDE/PZE).",
                "bemerkung": "Die Basis für jede Form flexibler Arbeit ist funktionierende Infrastruktur. Gerade in Cluster 1 fehlen häufig IT-Grundlagen, insbesondere im Werkstattbereich."
            },
            {
                "text": "Starten Sie mit klar umrissenen Digitalisierungsinseln – z. B. digitale Schichtpläne, Wartungslisten oder Urlaubsfreigaben für Teamleiter:innen.",
                "bemerkung": "Technikeinführungen sollten in etablierten Routinen ansetzen. Kleinprojekte mit sichtbarem Nutzen stärken Akzeptanz und Selbstvertrauen im Umgang mit IT."
            },
            {
                "text": "Nutzen Sie vorhandene Maschinendaten für einfache Visualisierungen (z. B. Stillstandsanalyse an CNC-Bearbeitungszentren) und koppeln Sie diese an einfache Dashboards.",
                "bemerkung": "Auch klassische Fertigungsbetriebe verfügen oft über verwertbare Steuerungsdaten. Eine erste Visualisierung kann Türöffner für datengestützte Verbesserungen sein."
            }
        ],
        "Organisation": [
            {
                "text": "Führen Sie niedrigschwellige Pilotmodelle für Zeitflexibilität ein – z. B. Gleitzeitkonten in AV oder verlängerte Pausenfenster im 1-Schichtbetrieb.",
                "bemerkung": "In reaktiven Betrieben fehlt oft die Erfahrung mit flexiblen Arbeitsformen. Kleinversuche mit klaren Spielregeln ermöglichen risikofreies Ausprobieren."
            },
            {
                "text": "Integrieren Sie Reflexionsroutinen (z. B. „Wo stehen wir mit Flexibilisierung?“-Check-ins in Teambesprechungen).",
                "bemerkung": "Reaktive Strukturen verändern sich selten von selbst. Kontinuierliche Reflexion verankert Flexibilisierung als gemeinsamen Lernprozess."
            },
            {
                "text": "Richten Sie eine bereichsübergreifende Steuerungsgruppe für mobile und zeitflexible Arbeit ein – mit Beteiligung von Betriebsrat, Produktion und Verwaltung.",
                "bemerkung": "Gerade in traditionell geführten Unternehmen braucht es transparente Strukturen, um Misstrauen abzubauen und gemeinsam handhabbare Lösungen zu erarbeiten."
            }
        ],
        "Kultur": [
            {
                "text": "Laden Sie gezielt externe Impulsgeber aus vergleichbaren Betrieben ein (z. B. Kurzvorträge, Betriebsbesichtigungen), die erste Schritte in Flexibilisierung gegangen sind.",
                "bemerkung": "Betriebe mit geringer Veränderungsdynamik profitieren von realitätsnahen Vorbildern. Externe Inputs wirken oft motivierender als interne Appelle."
            },
            {
                "text": "Führen Sie monatliche Teamrunden ein, in denen Arbeitsprobleme offen diskutiert werden dürfen – mit Fokus auf lösungsorientierter Kommunikation.",
                "bemerkung": "Eine offene Gesprächskultur ist Grundlage für jede Veränderung. In reaktiven Betrieben muss dies aktiv gefördert und moderiert werden."
            },
            {
                "text": "Entwickeln Sie gemeinsam mit Führungskräften ein internes Flexibilitätsleitbild – mit konkreten Beispielen aus dem Betriebsalltag.",
                "bemerkung": "Ein betriebsspezifisches Leitbild konkretisiert abstrakte Veränderungsziele und schafft Orientierung in kulturell gefestigten Strukturen."
            }
        ],
        "Mensch": [
            {
                "text": "Bieten Sie praxisnahe Kurzschulungen zur digitalen Anwendungskompetenz an (z. B. 30-Minuten-Workshops zu Excel, Zeiterfassung, Teams).",
                "bemerkung": "Viele Beschäftigte im Cluster 1 meiden digitale Anwendungen aus Unsicherheit. Kurze, alltagsnahe Formate senken Schwellen und fördern Selbstvertrauen."
            },
            {
                "text": "Stellen Sie eine Vertrauensperson oder Lotsen aus der Belegschaft bereit, die Kolleg:innen bei Fragen zur Selbstorganisation und Technik unterstützt.",
                "bemerkung": "Peer-Lernen ist in vertrauten Strukturen oft effektiver als formelle Schulung. Ein erfahrener Kollege oder eine Kollegin kann niedrigschwellige Hilfe bieten."
            },
            {
                "text": "Führen Sie individuelle Beratungssprechstunden zur Vereinbarkeit von Arbeitszeit und Privatleben ein – besonders für pflegende Angehörige und Eltern.",
                "bemerkung": "Flexibilisierung muss konkret anschlussfähig sein. Individuelle Lebenslagen lassen sich besser durch persönliche Gespräche als durch allgemeine Regelungen adressieren."
            }
        ]
    },

    "Cluster 2 – Produktionsstark, aber mobilitätsfern": {
        "Technik": [
            {
                "text": "Ermöglichen Sie sicheren Remote-Zugriff auf produktionsrelevante Systeme für indirekte Bereiche (z. B. AV, Konstruktion, Qualitätssicherung).",
                "bemerkung": "In diesem Cluster ist die technische Infrastruktur oft vorhanden, wird aber nicht für mobile Arbeit genutzt. VPN-Zugänge, mobile Clients oder Remote-Desktop-Lösungen schaffen eine direkte Anschlussfähigkeit."
            },
            {
                "text": "Stellen Sie produktionsnahe Dashboards bereit, die sowohl in der Fertigung als auch mobil verfügbar sind (z. B. Fertigungsstatus, Auftragsfortschritt, Rückmeldungen).",
                "bemerkung": "Produktionsstarke Betriebe profitieren von Transparenz über KPIs. Mobil verfügbare Dashboards fördern Vertrauen und ermöglichen ortsunabhängige Entscheidungen – ohne in Steuerungshoheit einzugreifen."
            },
            {
                "text": "Nutzen Sie CAD-, CAM- und Werkzeugdaten zentralisiert – mit Zugriffsmöglichkeiten von verschiedenen Standorten (z. B. Konstruktion, NC-Programmierung, AV).",
                "bemerkung": "Flexibilisierung in technischen Bereichen erfordert Zugriff auf zentrale Datenpools. Einheitliche Datenhaltung ist dafür technische Voraussetzung und organisatorische Entlastung zugleich."
            }
        ],
        "Organisation": [
            {
                "text": "Führen Sie hybridfähige Rollenanalysen durch – mit Fokus auf indirekte Bereiche und Schichtbegleitfunktionen (z. B. AV, IT, Produktionsplanung, Qualität).",
                "bemerkung": "Oft ist unklar, welche Aufgaben tatsächlich ortsunabhängig bearbeitet werden können. Eine strukturierte Analyse zeigt das Potenzial und hilft, realistische Flexibilisierungsmodelle zu entwickeln."
            },
            {
                "text": "Entwickeln Sie modularisierte Arbeitszeitmodelle – z. B. Früh-/Spät-Gleitzeitfenster oder rollierende Homeoffice-Tage für bestimmte Teams.",
                "bemerkung": "In produktionsgeprägten Betrieben ist Schichtstabilität zentral. Modularisierte Modelle ermöglichen dennoch zeitliche Spielräume ohne Verlust an Produktionssicherheit."
            },
            {
                "text": "Schaffen Sie organisatorische Schnittstellen für den Informationsaustausch zwischen mobilen und präsenten Beschäftigten (z. B. feste Abstimmfenster, digitale Boards).",
                "bemerkung": "Mobilität darf nicht zur Informationslücke führen. Klare, regelmäßige Austauschformate sichern Zusammenarbeit über Arbeitsorte hinweg ab."
            }
        ],
        "Kultur": [
            {
                "text": "Thematisieren Sie Mobilitäts- und Flexibilisierungsoptionen aktiv in Führungskreisen – auch mit kritischer Reflexion eigener Haltungen.",
                "bemerkung": "In diesem Cluster liegt das Haupthemmnis in der Kultur. Reflexion in der Führung zu Vertrauen, Kontrolle und Leistung ist ein zentraler Hebel für Veränderung."
            },
            {
                "text": "Stellen Sie positive Praxisbeispiele aus dem eigenen Unternehmen systematisch sichtbar dar – z. B. im Intranet, in Teammeetings oder über Aushänge.",
                "bemerkung": "Akzeptanz entsteht durch Vorbilder. Wenn erste Teams erfolgreich mobil arbeiten, kann dies Zweifel in anderen Bereichen reduzieren."
            },
            {
                "text": "Verankern Sie die Vereinbarkeit von Arbeit und Privatleben in bestehenden Führungs- und Zielvereinbarungssystemen.",
                "bemerkung": "Oft wird Vereinbarkeit nur kommunikativ, aber nicht systemisch gefördert. Die Integration in Zielsysteme zeigt Verbindlichkeit und steigert Führungssensibilität."
            }
        ],
        "Mensch": [
            {
                "text": "Führen Sie gezielte Schulungen zu digitalen Tools in den relevanten indirekten Bereichen durch – z. B. AV, Konstruktion, Qualitätssicherung.",
                "bemerkung": "Zwar besteht in diesem Cluster hohe technische Ausstattung, doch nicht alle Beschäftigten nutzen sie souverän. Tool-Schulungen stärken Handlungssicherheit für mobile Arbeit."
            },
            {
                "text": "Bieten Sie strukturierte Onboarding-Prozesse für mobile Arbeit an – z. B. mit Checklisten, Kontaktpersonen und klaren Kommunikationsstandards.",
                "bemerkung": "Viele Fachkräfte wissen nicht, was im Homeoffice erwartet wird. Ein strukturiertes Onboarding hilft, Unsicherheit zu reduzieren und Leistungserwartungen zu klären."
            },
            {
                "text": "Ermutigen Sie Teams zur Entwicklung eigener Flexibilitätsregeln – etwa zur Erreichbarkeit, Aufgabenteilung oder Feedbackkultur im mobilen Arbeiten.",
                "bemerkung": "Wenn Mitarbeitende eigene Regeln mitgestalten, steigt die Identifikation. Gleichzeitig wird die alltagsnahe Umsetzbarkeit gefördert."
            }
        ]
    },

    "Cluster 3 – Digital-affin und akzeptanzstark": {
        "Technik": [
            {
                "text": "Erweitern Sie bestehende Tools durch funktionsübergreifende Kollaborationsplattformen (z. B. MS Teams, Planner, Confluence).",
                "bemerkung": "In Cluster 3 sind Basistechnologien vorhanden. Der nächste Schritt besteht in der systematischen Integration und Nutzung von Kooperationsfunktionen über Team- und Abteilungsgrenzen hinweg."
            },
            {
                "text": "Digitalisieren Sie vollständig administrative Abläufe rund um Arbeitszeit, Urlaubsplanung und Schichtorganisation.",
                "bemerkung": "Die technischen Voraussetzungen sind in der Regel vorhanden. Automatisierte Prozesse steigern Transparenz und entlasten Führungskräfte und Mitarbeitende gleichermaßen."
            },
            {
                "text": "Verknüpfen Sie produktionsrelevante Datenquellen in Echtzeit (z. B. MDE/BDE/ERP mit Visualisierung für remote-Zugriffe).",
                "bemerkung": "Flexibilität braucht Datentransparenz. In digital-affinen Unternehmen können bestehende Systeme sinnvoll verknüpft werden, um ortsunabhängige Steuerung zu ermöglichen."
            }
        ],
        "Organisation": [
            {
                "text": "Etablieren Sie regelmäßige Review-Zyklen zur Reflexion und Weiterentwicklung flexibler Arbeit (z. B. halbjährliche Team-Workshops).",
                "bemerkung": "Cluster 3 zeichnet sich durch hohe Offenheit aus. Um Flexibilisierung langfristig erfolgreich zu gestalten, bedarf es strukturierter Feedback- und Weiterentwicklungsformate."
            },
            {
                "text": "Definieren Sie verbindliche Regelungen zu Erreichbarkeit, Arbeitszeiterfassung und Aufgabenverteilung in mobilen Settings.",
                "bemerkung": "Eine offene Arbeitskultur braucht zugleich verlässliche Strukturen. Klare Rahmenbedingungen fördern Vertrauen und Fairness im Team."
            },
            {
                "text": "Nutzen Sie hybride Betriebsvereinbarungen als lernende Regelwerke – mit offenen Evaluationsklauseln.",
                "bemerkung": "Flexibilisierung darf nicht im Experiment enden. Regelwerke mit Weiterentwicklungsoptionen helfen, Agilität und Verbindlichkeit zu vereinen."
            }
        ],
        "Kultur": [
            {
                "text": "Fördern Sie Eigenverantwortung durch mehr Entscheidungsspielräume bei Arbeitsort und -zeit – auf Teamebene abgestimmt.",
                "bemerkung": "Dieses Cluster ist bereit für Autonomie. Führung sollte Gestaltungsspielräume freigeben, dabei aber teaminterne Aushandlung unterstützen."
            },
            {
                "text": "Stärken Sie eine dialogische Führungskultur – z. B. durch Führungskräftefeedbacks oder Peer-Coachings.",
                "bemerkung": "Die Führungskultur ist bereits offen – sie kann durch gezielte Maßnahmen weiterentwickelt werden, um Ambiguitätstoleranz und Vertrauen zu festigen."
            },
            {
                "text": "Feiern Sie erfolgreiche Umsetzungen flexibler Arbeit sichtbar – z. B. durch interne Erfolgsgeschichten oder Anerkennungsformate.",
                "bemerkung": "Gelingen braucht Sichtbarkeit. Positive Beispiele stärken die kulturelle Akzeptanz und motivieren zur weiteren Ausweitung."
            }
        ],
        "Mensch": [
            {
                "text": "Nutzen Sie das Erfahrungswissen langjähriger Mitarbeitender für Mentoringformate im Umgang mit digital-flexibler Arbeit.",
                "bemerkung": "Die Belegschaft verfügt über vielfältige Erfahrung. Mentoring-Formate fördern Wissenstransfer und stärken soziale Bindung im hybriden Kontext."
            },
            {
                "text": "Fördern Sie Selbstlernkompetenzen durch Zugang zu E-Learning-Plattformen und individuelle Entwicklungsziele.",
                "bemerkung": "In diesem Cluster sind Lernbereitschaft und IT-Affinität hoch. Zielgerichtete Selbstlernformate stärken Eigenverantwortung und digitale Souveränität."
            },
            {
                "text": "Ergänzen Sie das Onboarding neuer Beschäftigter um Module zur Selbstorganisation im hybriden Arbeiten.",
                "bemerkung": "Gerade neue Mitarbeitende brauchen Orientierung. Onboarding-Prozesse sollten systematisch an digitale und flexible Arbeitsrealitäten angepasst werden."
            }
        ]
    },

   "Cluster 4 – Technisch solide, aber prozessual träge": {
        "Technik": [
            {
                "text": "Identifizieren Sie technische Engpässe in der Datenverfügbarkeit und beseitigen Sie Hürden für Echtzeittransparenz (z. B. fehlende Schnittstellen zwischen ERP und MES).",
                "bemerkung": "Obwohl Systeme vorhanden sind, fehlt oft die systematische Verbindung. Transparente Datenflüsse sind Grundvoraussetzung für Prozessoptimierung und Mobilität."
            },
            {
                "text": "Ergänzen Sie bestehende Steuerungstechnik durch einfache Assistenzsysteme, die auch mobil genutzt werden können (z. B. Tablet-Lösungen für AV oder QS).",
                "bemerkung": "In prozessual trägen Betrieben können Assistenzsysteme helfen, bestehende Technik effizienter zu nutzen – ohne direkt ganze Systeme umzustellen."
            },
            {
                "text": "Führen Sie technische Pilotprojekte zur digitalen Auftragsverfolgung in ausgewählten Bereichen durch.",
                "bemerkung": "Pilotprojekte mit überschaubarem Risiko ermöglichen technische Fortschritte, ohne den Gesamtprozess zu gefährden."
            }
        ],
        "Organisation": [
            {
                "text": "Entflechten Sie komplexe oder überlastete Kernprozesse – z. B. durch Prozessmapping und Identifikation nicht-wertschöpfender Tätigkeiten.",
                "bemerkung": "Prozessuale Trägheit entsteht oft aus überladenen Abläufen. Eine strukturierte Prozessanalyse zeigt Potenziale für Entschlackung und Flexibilität auf."
            },
            {
                "text": "Erstellen Sie Roadmaps für flexible Arbeit – mit konkreten Etappen, Verantwortlichkeiten und Evaluationszeitpunkten.",
                "bemerkung": "In technisch stabilen, aber trägen Betrieben braucht es Struktur. Roadmaps schaffen Orientierung und steigern Umsetzungswahrscheinlichkeit."
            },
            {
                "text": "Erproben Sie modulare Arbeitszeitmodelle zunächst in unterstützenden Bereichen (z. B. Qualitätssicherung, Instandhaltung).",
                "bemerkung": "Diese Bereiche haben oft ausreichend Freiheitsgrade. Erste Modelle dort wirken als Proof-of-Concept für spätere Ausweitung."
            }
        ],
        "Kultur": [
            {
                "text": "Stärken Sie Veränderungsbereitschaft durch interne Kommunikation über Erfolge anderer Bereiche (z. B. „Flexibilitäts-Funktionen des Monats“).",
                "bemerkung": "Kommunikation über Erfolge wirkt motivierend. In trägen Kulturen braucht es positive Reize zur Reaktivierung."
            },
            {
                "text": "Binden Sie die betriebliche Interessenvertretung frühzeitig in Transformationsprozesse ein – insbesondere bei Fragen der Flexibilisierung.",
                "bemerkung": "Vertrauensvolle Zusammenarbeit mit Gremien reduziert Blockaden und schafft gemeinsame Verantwortung für den Wandel."
            },
            {
                "text": "Führen Sie bewusst „Lernformate“ statt reine „Informationsformate“ ein – z. B. kurze Praxislabs zu flexiblen Arbeitsformen.",
                "bemerkung": "Erklärungen reichen nicht aus. Praxisnahe Lernräume fördern Beteiligung und Akzeptanz nachhaltig."
            }
        ],
        "Mensch": [
            {
                "text": "Stärken Sie individuelle Handlungsfähigkeit durch klare Rollendefinitionen und transparente Zielvorgaben.",
                "bemerkung": "In unklaren Prozessen hilft Orientierung. Klare Rollen geben Sicherheit und machen Flexibilität anschlussfähig."
            },
            {
                "text": "Befragen Sie Beschäftigte gezielt nach Unterstützungsbedarfen bei der Einführung flexibler Arbeit (z. B. anonyme Kurzbefragung).",
                "bemerkung": "Oft ist nicht bekannt, woran es hakt. Befragungen schaffen Sichtbarkeit und ermöglichen gezielte Maßnahmen."
            },
            {
                "text": "Benennen Sie Veränderungsbotschafter:innen aus der Belegschaft, die gute Erfahrungen mit Flexibilisierung gemacht haben.",
                "bemerkung": "Anerkannte Kolleg:innen können als Brückenbauer:innen zwischen Management und Belegschaft wirken – besonders in trägen Systemen."
            }
        ]
    }
}

#Mapping der Antworten
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
        "< 1 Tag": 1,
        "1–3 Tage": 2,
        "4–6 Tage": 3,
        "≥ 7 Tage": 4
    }
    return mapping.get(durchlaufzeit_str, np.nan)

def categorize_laufzeit(laufzeit_str):
    if laufzeit_str is None:
        return np.nan
    mapping = {
        "< 10 min": 1,
        "11–30 min": 2,
        "31–89 min": 3,
        "≥ 90 min": 4
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
        "T1.3 Am oder nahe dem Maschinenarbeitsplatz sind Bereiche für computergestützte Tätigkeiten und digitale Zusammenarbeit vorhanden.",
        "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich.",
        "T2.3 Prozess- und Maschinendaten stehen in Echtzeit digital zur Verfügung.",
        "T2.4 Fernüberwachung und -zugriff auf Maschinen sind möglich.",
        "T2.5 Werkzeuge und Betriebsmittel sind digital erfasst und jederzeit verfügbar.",
        "O1.2 Erfahrungswissen wird dokumentiert und digital zugänglich gemacht.",
        "O3.2 Beschäftigte können während der Maschinenlaufzeit digitale Aufgaben (z. B. Programmierung, Dokumentation, Datenpflege) durchführen.",
        "O3.4 Qualitätssicherungsprozesse sind automatisisert im Fertigungsprozess möglich.",
        "O3.5 Auftragssteuerung ist digital unterstützt und dynamisch anpassbar.",
    ],
    
    # 7. Prozessinstabilität
    "Prozessinstabilität": [
        "T1.1 Zerspanende Fertigungsprozesse sind störungsarm.",
        "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "O1.1 Informationen zu Planung, Schichtübergaben und Störfällen sind digital und zeitnah verfügbar.",
        "O3.2 Beschäftigte können während der Maschinenlaufzeit digitale Aufgaben (z. B. Programmierung, Dokumentation, Datenpflege) durchführen",
        "O3.3 Lauf- und Durchlaufzeiten sind planbar und stabil steuerbar.",
        "O3.4 Qualitätssicherungsprozesse sind automatisisert im Fertigungsprozess möglich.",
    ],
    
    # 8. Nutzen (Wahrgenommener Nutzen von Flexibilität)
    "Nutzen": [
        "M1.1 Anforderungen an mobile Arbeit werden systematisch vermittelt (z. B. durch Schulungen oder Leitfäden).",
        "M1.2 Voraussetzungen und Grenzen zeitflexibler Arbeit werden klar kommuniziert.",
        "O3.2 Beschäftigte können während der Maschinenlaufzeit digitale Aufgaben (z. B. Programmierung, Dokumentation, Datenpflege) durchführen.",
        "O3.6 Produktivitäts- und Qualitätskennzahlen werden regelmäßig analysiert und für Verbesserungen genutzt.",
        "K1.3 Zielerreichung und Ergebnisse stehen vor physischer Anwesenheit.",
        "K1.4 Herausforderungen und Zielkonflikte flexibler Arbeit werden offen angesprochen und reflektiert.",
        "K2.1 Die Unternehmensführung lebt flexible Arbeitsformen sichtbar vor und positioniert sich aktiv dazu.",
        "K2.2 Führungskräfte unterstützen flexible Arbeitsformen aktiv und führen ergebnisorientiert."
    ],
    
    # 9. Akzeptanz
    "Akzeptanz": [
        "M2.1 Beschäftigte zeigen Offenheit gegenüber mobiler Arbeit.",
        "M2.2 Beschäftigte zeigen Offenheit gegenüber zeitflexibler Arbeit.",
        "M2.5 Beschäftigte verstehen automatisierte Produktionssysteme und digitale Prozesse in ihren wesentlichen Funktionen.",
        "M2.6 Beschäftigte stehen neuen, digital vernetzten Technologien und Abläufen offen und veränderungsbereit gegenüber.",
        "O1.4 Erwartungen an dauerhafte Erreichbarkeit sind klar geregelt und werden begrenzt.",
        "O2.2 Verbindliche Betriebsvereinbarungen zu mobiler und zeitflexibler Arbeit bestehen.",
        "O3.6 Produktivitäts- und Qualitätskennzahlen werden regelmäßig analysiert und für Verbesserungen genutzt.",
        "K1.1 Vertrauen bildet die Grundlage der Zusammenarbeit.",
        "K2.1 Die Unternehmensführung lebt flexible Arbeitsformen sichtbar vor und positioniert sich aktiv dazu."
    ],
    
    # 10. Aufwand Zeit (Wahrgenommener Zeitaufwand für flexible Arbeit)
    # HINWEIS: Bei der Berechnung dieser Variablen wird der Wert inbvertiert, da ein höherer Score in der Frage ("können mitgestalten") einen niedrigeren "Aufwand Zeit" für das Cluster bedeutet.
    "Aufwand Zeit": [
        "M1.2 Voraussetzungen und Grenzen zeitflexibler Arbeit werden klar kommuniziert.",
        "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "T1.4 Fertigungsprozesse sind standardisiert dokumentiert.",
        "M1.4 Die betriebliche Kompetenzentwicklung fördert gezielt die Selbstorganisation und Entscheidungsfähigkeit im Rahmen flexibler Arbeit.",
        "O1.1 Informationen zu Planung, Schichtübergaben und Störfällen sind digital und zeitnah verfügbar.",
        "O2.1 Rechtliche Vorgaben zu flexibler Arbeit sind bekannt und werden eingehalten.",
        "O2.2 Verbindliche Betriebsvereinbarungen zu mobiler und zeitflexibler Arbeit bestehen.",
        "O2.3 Die Personalplanung berücksichtigt flexible Arbeitszeiten.",
        "O2.7 Arbeitszeitkonten oder vergleichbare Systeme werden aktiv genutzt.",
        "O2.5 Beschäftigte können Beginn und Ende ihrer Arbeitszeit innerhalb festgelegter Grenzen selbst bestimmen.",
        "O2.7 Arbeitszeitkonten oder vergleichbare Systeme werden aktiv genutzt.",
        "K2.1 Die Unternehmensführung lebt flexible Arbeitsformen sichtbar vor und positioniert sich aktiv dazu."
    ],
    
    # 11. Aufwand Mobil (Wahrgenommener Aufwand für mobiles Arbeiten)
    # HINWEIS: Wird auch invertiert (Siehe Aufwand Zeit)
    "Aufwand Mobil": [
        "M1.1 Anforderungen an mobile Arbeit werden systematisch vermittelt (z. B. durch Schulungen oder Leitfäden).",
        "M1.3 Beschäftigte erhalten gezielte Unterstützung, um bei Prozessabweichungen eigenverantwortlich und sicher zu handeln.",
        "M2.3 Beschäftigte verfügen über die Fähigkeit, ihre Arbeit eigenständig zu strukturieren und zu organisieren.",
        "T1.1 Zerspanende Fertigungsprozesse sind störungsarm.",
        "T1.2 Werkzeugmaschinen können ohne ständige Anwesenheit betrieben werden.",
        "T1.3 Am oder nahe dem Maschinenarbeitsplatz sind Bereiche für computergestützte Tätigkeiten und digitale Zusammenarbeit vorhanden.",
        "T2.1 Mobile Endgeräte stehen für mobile Arbeit zur Verfügung.",
        "T2.2 Der Zugriff auf relevante Systeme (z. B. ERP, MES) ist ortsunabhängig und sicher möglich.",
        "T2.4 Fernüberwachung und -zugriff auf Maschinen sind möglich.",
        "T2.6 Der IT-Support kann auch produktionsbezogene IT-Probleme beheben.",
        "T2.7 IT-Sicherheitskonzepte sind etabliert und werden regelmäßig geprüft.",
        "O2.1 Rechtliche Vorgaben zu flexibler Arbeit sind bekannt und werden eingehalten.",
        "O2.2 Verbindliche Betriebsvereinbarungen zu mobiler und zeitflexibler Arbeit bestehen.",
        "O2.4 Die Personalplanung berücksichtigt flexible Arbeitsorte.",
        "O3.1 Aufgaben sind hinsichtlich ihrer Präsenzbindung analysiert und systematisch aufteilbar.",
        "K2.1 Die Unternehmensführung lebt flexible Arbeitsformen sichtbar vor und positioniert sich aktiv dazu."
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
    "Weitgehend erfüllt": 3,
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
    .text-box {
        padding: 1.2rem;
        background-color: #f0f0f0;
        border-left: 5px solid #0066cc;
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        font-size: 17px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="text-box">
    <p><strong>Die Digitalisierung</strong> und der <strong>Wunsch nach flexibleren Arbeitsmodellen</strong> stellen produzierende Unternehmen vor neue Herausforderungen. Wie können beispielsweise Homeoffice und flexible Arbeitszeiten in der Produktion umgesetzt werden? Das entwickelte <strong>Diagnose- und Entwicklungsmodell</strong> hilft Ihnen dabei, diese Frage systematisch anzugehen: Es zeigt Ihnen, wo Ihr Unternehmen heute steht und gibt Ihnen konkrete <strong>Handlungsempfehlungen</strong> für die Umsetzung flexibler Arbeitsformen an die Hand.</p>

    <p>Das Modell wurde speziell für <strong>Unternehmen der zerspanenden Fertigung</strong> entwickelt. Es ermöglicht Ihnen eine <strong>strukturierte Bestandsaufnahme</strong> Ihres Unternehmens und zeigt gleichzeitig auf, wie Sie die <strong>Einführung mobiler und zeitflexibler Arbeit</strong> unterstützen können. Dabei berücksichtigt das Modell vier wichtige Bereiche: Ihre <strong>Beschäftigten</strong>, die vorhandene <strong>Technik</strong>, Ihre <strong>Organisation</strong> und die <strong>Unternehmenskultur</strong>. Diese vier Bereiche werden in neun <strong>konkrete Handlungsfelder</strong> unterteilt, die speziell auf die Besonderheiten der zerspanenden Fertigung zugeschnitten sind.</p>
    
    <p><strong>Die Bewertung basiert auf einem vierstufigen System:</strong></p>
    <ul>
        <li><strong>Stufe 1 – Nicht erfüllt:</strong> Dieses Kriterium wird derzeit nicht umgesetzt.</li>
        <li><strong>Stufe 2 – Teilweise erfüllt:</strong> Erste Ansätze sind vorhanden, aber noch nicht systematisch.</li>
        <li><strong>Stufe 3 – Weitgehend erfüllt:</strong> Das Kriterium ist größtenteils umgesetzt und funktioniert.</li>
        <li><strong>Stufe 4 – Vollständig erfüllt:</strong> Das Kriterium ist vollständig umgesetzt und fest etabliert.</li>
    </ul>

    <p>Nach der Selbstbewertung erhalten Sie ein übersichtliches <strong>grafisches Profil</strong>, das Ihre Stärken und Verbesserungsmöglichkeiten auf einen Blick zeigt. Das System ordnet Ihr Unternehmen automatisch einem von <strong>vier Unternehmenstypen</strong> zu, die aus der Praxis abgeleitet wurden. Basierend auf diesem Typ bekommen Sie maßgeschneiderte, <strong>praxisnahe Handlungsempfehlungen</strong>, die Ihnen konkrete nächste Schritte für die Weiterentwicklung Ihrer Arbeitsorganisation aufzeigen.</p>
    </div>
    """, unsafe_allow_html=True)

#Fragenblock
elif current_tab in mtok_structure:
    dimension = current_tab
    for feld in mtok_structure[dimension]:
        st.subheader(f"Handlungsfeld: {feld}")
        if feld in einleitungstexte:
            st.markdown(
                f"<div style='font-size:18px; color:#333; margin-bottom:1.2rem;line-height:1.5;'>{einleitungstexte[feld]}</div>",
                unsafe_allow_html=True
            )

        scores_for_this_hf = []

        for idx, item in enumerate(Kriterien.get(feld, [])):
            frage_text = html.escape(item["frage"])
            begruendung = html.escape(item["begründung"])

            radio_key = f"{dimension}_{feld}_{idx}"
            score_key = f"{radio_key}_score"

            # Initialisiere Mapping einmalig
            if "item_to_radio_key_map" not in st.session_state:
                st.session_state["item_to_radio_key_map"] = {}
            st.session_state["item_to_radio_key_map"][item['frage']] = score_key

            # Optionen je nach Einschränkung
            einschraenkung = item.get("einschraenkung", None)
            if einschraenkung == "1_und_4":
                options = ["Nicht erfüllt", "Vollständig erfüllt"]
            else:
                options = ["Nicht erfüllt", "Teilweise erfüllt", "Weitgehend erfüllt", "Vollständig erfüllt"]

            # Vorherige Auswahl berücksichtigen
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

            # Container zur Gruppierung
            with st.container():
                st.markdown(f"""
                    <div class="evaluation-question">{frage_text}</div>
                    <div class="evaluation-info">{begruendung}</div>
                """, unsafe_allow_html=True)

                auswahl = st.radio(
                    label="",
                    options=options,
                    key=radio_key,
                    index=default_index,
                    label_visibility="collapsed"
                )        

                st.markdown("""
                <hr style='
                    border: none;
                    border-top: 1px solid #ccc;
                    margin-top: 2rem;
                    margin-bottom: 2rem;
                '>
                """, unsafe_allow_html=True)

            # Score speichern
            score = score_mapping.get(auswahl, np.nan)
            st.session_state[score_key] = score
            scores_for_this_hf.append(score)

        # Mittelwert pro Handlungsfeld speichern
        if any(~np.isnan(scores_for_this_hf)):
            if "ergebnisse" not in st.session_state:
                st.session_state["ergebnisse"] = {}
            st.session_state.ergebnisse[feld] = np.nanmean(scores_for_this_hf)
        else:
            if "ergebnisse" in st.session_state and feld in st.session_state.ergebnisse:
                del st.session_state.ergebnisse[feld]

        # ⬇️ Einzelantworten (nur Score) speichern
        if "einzel_scores" not in st.session_state:
            st.session_state["einzel_scores"] = {}

        for idx, item in enumerate(Kriterien.get(feld, [])):
            radio_key = f"{dimension}_{feld}_{idx}_score"
            score = st.session_state.get(radio_key, 9999)

            if isinstance(score, float) and np.isnan(score):
                score = 9999

            st.session_state["einzel_scores"][f"{feld}__{idx}"] = score

#Abschließende Fragen
elif current_tab == "Abschließende Fragen":
    st.subheader("Spezifische technische und prozessuale Angaben")

    def radio_with_categorization(frage, options, key, categorize_func):
        vorhandene_auswahl = st.session_state.get(key, None)

        try:
            default_index = options.index(vorhandene_auswahl) if vorhandene_auswahl in options else 0
        except ValueError:
            default_index = 0

        with st.container():
            st.markdown(f"""
                <div class="evaluation-question">{frage}</div>
            """, unsafe_allow_html=True)

            auswahl = st.radio(
                label="",
                options=options,
                index=default_index,
                key=f"{key}_temp",
                label_visibility="collapsed"
            )

            # horizontale Linie am Ende
            st.markdown("""
                <hr style='
                    border: none;
                    border-top: 1px solid #ccc;
                    margin-top: 1.5rem;
                    margin-bottom: 2rem;
                '>
            """, unsafe_allow_html=True)

        # Speicherung in Session State
        st.session_state[key] = auswahl
        st.session_state[f"{key}_score"] = categorize_func(auswahl)

    # Fragenaufrufe
    radio_with_categorization(
        "A1.1 Wie viele CNC-Werkzeugmaschinen haben Sie in Ihrer zerspanenden Fertigung?",
        ["< 5", "5-10", "11-24", "≥ 25"],
        "cnc_range",
        categorize_cnc_machines
    )

    radio_with_categorization(
        "A1.2 Wie viel Prozent Ihrer CNC-Werkzeugmaschinen besitzen eine Automation für den Werkstückwechsel?",
        ["0%", "1-25%", "26-49%", "≥ 50%"],
        "automation_range",
        categorize_automation_percentage
    )

    radio_with_categorization(
        "A1.3 Welche durchschnittlichen Losgrößen werden bei Ihnen gefertigt?",
        ["< 5", "5-50", "51-99", "≥ 100"],
        "losgroesse_range",
        categorize_losgroesse
    )

    radio_with_categorization(
        "A1.4 Welche durchschnittliche Laufzeit haben die Werkstücke, die bei Ihnen gefertigt werden?",
        ["< 10 min", "11–30 min", "31–89 min", "≥ 90 min"],
        "laufzeit_range",
        categorize_laufzeit
    )
    
    radio_with_categorization(
        "A1.5 Wie lang ist die durchschnittliche Durchlaufzeit (von Rohmaterial bis zum unentgrateten Fertigteil) eines Auftrags über alle Maschinen?",
        ["< 1 Tag", "1–3 Tage", "4–6 Tage", "≥ 7 Tage"],
        "durchlaufzeit_range",
        categorize_durchlaufzeit
    )

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
            st.subheader("Unternehmens-Profil")
            # Reihenfolge für MTOK-Struktur (Uhrzeigersinn)
            labels_ordered = [
                "Qualifikation und Kompetenzentwicklung (Mensch)",
                "Persönliches Voraussetzungen (Mensch)",
                "Automatisierung und Arbeitsplatzgestaltung (Technik)",
                "Digitale Vernetzung und IT-Infrastruktur (Technik)",
                "Kommunikation, Kooperation und Zusammenarbeit (Organisation)",
                "Organisatorische Umwelt (Organisation)",
                "Produktionsorganisation (Organisation)",
                "Unternehmenskultur (Kultur)",
                "Führung und Teamzusammenhalt (Kultur)"
            ]

            # Werte entsprechend sortieren (achte auf die korrekte Reihenfolge)
            values_ordered = [
                st.session_state.ergebnisse.get("Qualifikation und Kompetenzentwicklung", 1),
                st.session_state.ergebnisse.get("Persönliche Voraussetzungen", 1),
                st.session_state.ergebnisse.get("Automatisierung und Arbeitsplatzgestaltung", 1),
                st.session_state.ergebnisse.get("Arbeitsplatzgestaltung und ", 1),
                st.session_state.ergebnisse.get("Kommunikation, Kooperation und Zusammenarbeit", 1),
                st.session_state.ergebnisse.get("Organisatorische Umwelt", 1),
                st.session_state.ergebnisse.get("Produktionsorganisation", 1),
                st.session_state.ergebnisse.get("Unternehmenskultur", 1),
                st.session_state.ergebnisse.get("Führung und Teamzusammenhalt", 1)
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
            #ax.set_title("Cluster-Profil", fontsize=14, pad=20)

            # Ausgabe in Streamlit
            # Radar-Diagramm als PNG speichern und gleichzeitig Base64-kodieren
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
            buf.seek(0)

            # Für die Streamlit-Anzeige
            st.image(buf, width=700)

            # Für den HTML-Export: Base64 umwandeln
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode("utf-8")
            radar_html = f'<img src="data:image/png;base64,{image_base64}" alt="Radar-Diagramm" width="600"/>'
    
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

            st.info(cluster_beschreibungen.get(cluster_result, "Keine Beschreibung verfügbar."))

            # Bild für das aktuelle Cluster anzeigen
            bild_pfad = cluster_bilder.get(cluster_result)
            if bild_pfad:
                st.image(bild_pfad, caption=cluster_result, width=400)

            # Handlungsempfehlungen nach Cluster und MTOK
            st.subheader("Clusterspezifische Handlungsempfehlungen")

            cluster_empfehlungen = handlungsempfehlungen.get(cluster_result, {})

            for dimension in ["Technik", "Organisation", "Kultur", "Mensch"]:
                if dimension in cluster_empfehlungen:
                    st.markdown(f"### {dimension}")
                    for eintrag in cluster_empfehlungen[dimension]:
                        st.markdown(f"""
            <div style='margin-bottom: 22px;'>
                <strong>➤ {eintrag['text']}</strong><br>
                <span style='color:#444; font-size: 94%; font-weight: normal;'>{eintrag['bemerkung']}</span>
            </div>
            """, unsafe_allow_html=True)
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
                    empfehlungs_block = "<ul>"
                    for eintrag in cluster_empfehlungen[dimension]:
                        empfehlungs_block += f"""
                        <li>
                            <strong>{eintrag['text']}</strong><br>
                            <span style='font-size: 90%; color: #555;'>{eintrag['bemerkung']}</span>
                        </li>
                        """
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
                <h2>Unternehmens-Profil</h2>
                {radar_html}
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

#Evaluationsfragen
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
            "Qualifikation und Kompetenzentwicklung",
            "Persönliche Voraussetzungen",
            "Automatisierung und Arbeitsplatzgestaltung",
            "Digitale Vernetzung und IT-Infrastruktur",
            "Kommunikation, Kooperation und Zusammenarbeit",
            "Organisatorische Umwelt",
            "Produktionsorganisation",
            "Unternehmenskultur",
            "Führung und Teamzusammenhalt"
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
        for key, score in st.session_state.get("einzel_scores", {}).items():
            daten_gesamt[f"{key}__score"] = score
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
