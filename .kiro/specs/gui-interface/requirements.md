# Requirements Document

## Introduction

Interfejs graficzny dla Make It Heavy ma zapewnić użytkownikom intuicyjny i nowoczesny sposób interakcji z systemem multi-agentowym. Aplikacja będzie zbudowana w Pythonie z wykorzystaniem biblioteki GUI (Tkinter lub PyQt/PySide) i będzie działać na macOS (Intel), oferując funkcjonalność podobną do nowoczesnych aplikacji chat, umożliwiając łatwe przełączanie między dostawcami AI, trybami pracy oraz zarządzanie kluczami API.

## Technical Requirements

- **Language**: Python 3.8+ (zgodnie z istniejącym projektem)
- **GUI Framework**: Tkinter (wbudowany) lub PyQt/PySide dla bardziej zaawansowanego UI
- **Integration**: Bezpośrednia integracja z istniejącymi modułami (agent.py, orchestrator.py, make_it_heavy.py, main.py)
- **Configuration**: Wykorzystanie istniejącego systemu konfiguracji YAML
- **Dependencies**: Minimalne dodatkowe zależności, wykorzystanie istniejących bibliotek projektu

## Requirements

### Requirement 1

**User Story:** Jako użytkownik, chcę mieć nowoczesny interfejs graficzny, aby móc wygodnie korzystać z Make It Heavy bez konieczności używania terminala.

#### Acceptance Criteria

1. WHEN aplikacja zostanie uruchomiona THEN system SHALL wyświetlić okno główne z interfejsem podobnym do nowoczesnego chatu
2. WHEN użytkownik uruchomi aplikację na macOS (Intel) THEN system SHALL działać płynnie i stabilnie
3. WHEN użytkownik zobaczy interfejs THEN system SHALL prezentować czytelny i intuicyjny design zgodny z macOS design guidelines

### Requirement 2

**User Story:** Jako użytkownik, chcę móc skonfigurować klucze API dla różnych dostawców, aby mieć dostęp do usług DeepSeek i OpenRouter.

#### Acceptance Criteria

1. WHEN użytkownik kliknie opcję konfiguracji API THEN system SHALL wyświetlić formularz do wprowadzenia kluczy API
2. WHEN użytkownik wprowadzi klucz API dla DeepSeek THEN system SHALL zapisać go bezpiecznie w konfiguracji
3. WHEN użytkownik wprowadzi klucz API dla OpenRouter THEN system SHALL zapisać go bezpiecznie w konfiguracji
4. IF klucz API jest nieprawidłowy THEN system SHALL wyświetlić komunikat o błędzie
5. WHEN klucze API zostaną zapisane THEN system SHALL umożliwić ich edycję w przyszłości

### Requirement 3

**User Story:** Jako użytkownik, chcę móc przełączać między dostawcami AI, aby wybrać najlepszy model dla mojego zadania.

#### Acceptance Criteria

1. WHEN użytkownik zobaczy interfejs THEN system SHALL wyświetlić opcję wyboru dostawcy (DeepSeek/OpenRouter)
2. WHEN użytkownik wybierze DeepSeek THEN system SHALL przełączyć konfigurację na DeepSeek API
3. WHEN użytkownik wybierze OpenRouter THEN system SHALL przełączyć konfigurację na OpenRouter API
4. IF wybrany dostawca nie ma skonfigurowanego klucza API THEN system SHALL wyświetlić komunikat o konieczności konfiguracji

### Requirement 4

**User Story:** Jako użytkownik, chcę móc wybierać konkretny model LLM od wybranego dostawcy, aby dostosować możliwości AI do specyficznych potrzeb zadania.

#### Acceptance Criteria

1. WHEN użytkownik wybierze dostawcy THEN system SHALL pobrać i wyświetlić listę dostępnych modeli od tego dostawcy
2. WHEN lista modeli zostanie załadowana THEN system SHALL wyświetlić ją w formie dropdown/select
3. WHEN użytkownik wybierze konkretny model THEN system SHALL skonfigurować go do użycia w zapytaniach
4. IF pobieranie listy modeli nie powiedzie się THEN system SHALL wyświetlić domyślne modele dla danego dostawcy
5. WHEN użytkownik przełączy dostawcę THEN system SHALL automatycznie załadować listę modeli dla nowego dostawcy

### Requirement 5

**User Story:** Jako użytkownik, chcę móc wybierać między trybem pojedynczego agenta a trybem heavy, aby dostosować sposób pracy do złożoności zadania.

#### Acceptance Criteria

1. WHEN użytkownik zobaczy interfejs THEN system SHALL wyświetlić opcję wyboru trybu (Single Agent/Heavy Mode)
2. WHEN użytkownik wybierze Single Agent THEN system SHALL skonfigurować wykonanie z użyciem main.py
3. WHEN użytkownik wybierze Heavy Mode THEN system SHALL skonfigurować wykonanie z użyciem make_it_heavy.py
4. WHEN tryb zostanie zmieniony THEN system SHALL wyświetlić informację o aktualnie wybranym trybie
5. WHEN użytkownik wybierze Heavy Mode THEN system SHALL wyświetlić informację o użyciu 4 równoległych agentów

### Requirement 6

**User Story:** Jako użytkownik, chcę mieć okno dialogowe do komunikacji z agentami, aby móc zadawać pytania i otrzymywać odpowiedzi w sposób podobny do chatu.

#### Acceptance Criteria

1. WHEN użytkownik zobaczy interfejs THEN system SHALL wyświetlić obszar do wpisywania wiadomości
2. WHEN użytkownik wpisze wiadomość i naciśnie Enter THEN system SHALL wysłać zapytanie do wybranego agenta/agentów
2.5 WHEN uzytkownik wcisnie shift i enter THEN zmiana wiersza
3. WHEN agent przetwarza zapytanie THEN system SHALL wyświetlić wskaźnik ładowania/progress
4. WHEN agent zwróci odpowiedź THEN system SHALL wyświetlić ją w obszarze konwersacji
5. WHEN używany jest Heavy Mode THEN system SHALL wyświetlić postęp pracy wszystkich 4 agentów
6. WHEN konwersacja się wydłuży THEN system SHALL umożliwić przewijanie historii wiadomości

### Requirement 7

**User Story:** Jako użytkownik, chcę mieć wizualnie atrakcyjny interfejs, aby praca z aplikacją była przyjemna i profesjonalna.

#### Acceptance Criteria

1. WHEN aplikacja zostanie uruchomiona THEN system SHALL wyświetlić interfejs z nowoczesnym designem
2. WHEN użytkownik zobaczy interfejs THEN system SHALL prezentować spójną kolorystykę i typografię
3. WHEN użytkownik korzysta z aplikacji THEN system SHALL zapewnić płynne animacje i przejścia
4. WHEN aplikacja działa na macOS THEN system SHALL używać natywnych elementów UI zgodnych z macOS
5. IF użytkownik ma włączony dark mode THEN system SHALL automatycznie dostosować się do ciemnego motywu
6. WHEN użytkownik zmienia rozmiar okna THEN system SHALL responsywnie dostosować layout

### Requirement 8

**User Story:** Jako użytkownik, chcę mieć możliwość zarządzania sesjami i historią, aby móc wracać do poprzednich konwersacji.

#### Acceptance Criteria

1. WHEN użytkownik rozpocznie nową konwersację THEN system SHALL utworzyć nową sesję
2. WHEN użytkownik zamknie aplikację THEN system SHALL zapisać historię konwersacji
3. WHEN użytkownik ponownie uruchomi aplikację THEN system SHALL umożliwić dostęp do poprzednich sesji
4. WHEN użytkownik wybierze poprzednią sesję THEN system SHALL przywrócić historię konwersacji
5. WHEN użytkownik chce wyczyścić historię THEN system SHALL umożliwić usunięcie wybranych sesji