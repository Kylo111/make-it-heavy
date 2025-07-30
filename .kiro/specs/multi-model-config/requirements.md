# Requirements Document

## Introduction

System konfiguracji wielu modeli dla Make It Heavy umożliwi użytkownikom przypisanie różnych modeli AI do poszczególnych agentów w trybie multiagent. System będzie zawierał GUI do łatwego zarządzania konfiguracją, automatyczne pobieranie informacji o kosztach od dostawców API oraz filtrowanie modeli obsługujących function calling.

## Requirements

### Requirement 1

**User Story:** Jako użytkownik Make It Heavy, chcę móc przypisać różne modele AI do poszczególnych agentów, aby zoptymalizować wydajność i koszty dla różnych typów zadań.

#### Acceptance Criteria

1. WHEN użytkownik otwiera konfigurację agentów THEN system SHALL wyświetlić listę 4 agentów z możliwością wyboru modelu dla każdego
2. WHEN użytkownik wybiera model dla agenta THEN system SHALL zapisać konfigurację w formacie YAML
3. WHEN użytkownik nie wybierze modelu dla agenta THEN system SHALL używać modelu domyślnego z głównej konfiguracji
4. WHEN użytkownik uruchomi tryb make-it-heavy THEN każdy agent SHALL używać przypisanego mu modelu

### Requirement 2

**User Story:** Jako użytkownik, chcę widzieć koszty input/output dla każdego modelu, aby móc podejmować świadome decyzje finansowe przy wyborze modeli.

#### Acceptance Criteria

1. WHEN użytkownik przegląda dostępne modele THEN system SHALL wyświetlić koszt za 1M tokenów input i output dla każdego modelu
2. WHEN system pobiera informacje o kosztach THEN dane SHALL być importowane bezpośrednio od dostawcy API (OpenRouter/DeepSeek)
3. WHEN koszt modelu nie jest dostępny THEN system SHALL wyświetlić "Koszt niedostępny"
4. WHEN użytkownik wybiera model THEN system SHALL pokazać szacunkowy koszt dla typowego zapytania

### Requirement 3

**User Story:** Jako użytkownik, chcę mieć dostęp tylko do modeli obsługujących function calling, aby zapewnić kompatybilność z systemem narzędzi Make It Heavy.

#### Acceptance Criteria

1. WHEN system ładuje listę dostępnych modeli THEN SHALL filtrować tylko modele z obsługą function calling
2. WHEN model nie obsługuje function calling THEN system SHALL wykluczyć go z listy wyboru
3. WHEN użytkownik próbuje wybrać niekompatybilny model THEN system SHALL wyświetlić komunikat o błędzie
4. WHEN system sprawdza kompatybilność THEN SHALL używać metadanych od dostawcy API

### Requirement 4

**User Story:** Jako użytkownik, chcę mieć intuicyjny GUI do zarządzania konfiguracją modeli, aby łatwo konfigurować system bez edytowania plików YAML.

#### Acceptance Criteria

1. WHEN użytkownik otwiera GUI konfiguracji THEN system SHALL wyświetlić przejrzysty interfejs z kartami dla każdego agenta
2. WHEN użytkownik wybiera model z dropdown THEN system SHALL pokazać szczegóły modelu (koszt, opis, możliwości)
3. WHEN użytkownik zapisuje konfigurację THEN system SHALL walidować wybrane modele i zapisać do pliku config
4. WHEN użytkownik resetuje konfigurację THEN system SHALL przywrócić ustawienia domyślne

### Requirement 5

**User Story:** Jako użytkownik, chcę widzieć podgląd całkowitych kosztów dla konfiguracji, aby móc porównać różne kombinacje modeli.

#### Acceptance Criteria

1. WHEN użytkownik konfiguruje modele THEN system SHALL obliczać szacunkowy koszt całkowity dla typowego zapytania
2. WHEN użytkownik zmienia model agenta THEN system SHALL natychmiast aktualizować kalkulację kosztów
3. WHEN system oblicza koszty THEN SHALL uwzględniać różne role agentów (research, analysis, verification, synthesis)
4. WHEN użytkownik porównuje konfiguracje THEN system SHALL pokazać różnicę w kosztach

### Requirement 6

**User Story:** Jako użytkownik, chcę mieć predefiniowane profile konfiguracji, aby szybko wybierać między różnymi strategiami (budget, balanced, premium).

#### Acceptance Criteria

1. WHEN użytkownik otwiera konfigurację THEN system SHALL oferować predefiniowane profile: Budget, Balanced, Premium
2. WHEN użytkownik wybiera profil Budget THEN system SHALL przypisać najtańsze kompatybilne modele
3. WHEN użytkownik wybiera profil Premium THEN system SHALL przypisać najlepsze dostępne modele
4. WHEN użytkownik wybiera profil Balanced THEN system SHALL zbalansować koszt i jakość

### Requirement 7

**User Story:** Jako użytkownik, chcę móc testować konfigurację przed jej zastosowaniem, aby upewnić się że wszystkie modele działają poprawnie.

#### Acceptance Criteria

1. WHEN użytkownik konfiguruje modele THEN system SHALL oferować opcję "Test Configuration"
2. WHEN użytkownik uruchamia test THEN system SHALL wykonać próbne zapytanie do każdego skonfigurowanego modelu
3. WHEN test się powiedzie THEN system SHALL wyświetlić potwierdzenie dla każdego agenta
4. WHEN test się nie powiedzie THEN system SHALL pokazać szczegóły błędu i sugestie rozwiązania

### Requirement 8

**User Story:** Jako użytkownik, chcę mieć możliwość eksportu i importu konfiguracji, aby móc dzielić się ustawieniami z innymi użytkownikami.

#### Acceptance Criteria

1. WHEN użytkownik eksportuje konfigurację THEN system SHALL utworzyć plik JSON z wszystkimi ustawieniami modeli
2. WHEN użytkownik importuje konfigurację THEN system SHALL walidować kompatybilność i zastosować ustawienia
3. WHEN importowana konfiguracja zawiera niekompatybilne modele THEN system SHALL pokazać ostrzeżenia
4. WHEN użytkownik dzieli konfigurację THEN system SHALL ukryć wrażliwe dane (API keys)