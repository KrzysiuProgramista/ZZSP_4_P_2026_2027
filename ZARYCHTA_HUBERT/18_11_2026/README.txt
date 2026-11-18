Zaawansowany SQL — rozwiązania A i B

A. Raport aktywności źródeł
A_raport.sql zawiera widok source_activity_report, objaśnienie jednostki
wiersza i progów, porównanie z allowlistą przez EXCEPT oraz wyniki
z dołączonej bazy. Otwórz network_security.db w DB Browser for SQLite
i uruchom poszczególne zapytania z zakładki Execute SQL. Widok jest już
zapisany w dołączonej kopii bazy. Raport obejmuje 13 IP i 896 zdarzeń.

B. Import i audyt
Po rozpakowaniu uruchom w terminalu: python B_import.py
Wymagany jest Python 3.10 lub nowszy. Skrypt korzysta z biblioteki
standardowej i wykonuje testy na dwóch kopiach SQLite w pamięci.
B_weryfikacja.sql zawiera zapytania użyte do inspekcji schematu, testu
triggera i porównania planów. B_wyniki.txt to zapis rzeczywistego uruchomienia.

Klucz importu: SHA-256 surowych pól CSV w kolejności z nagłówka,
połączonych znakiem |. sensor_name jest mapowana na istniejący sensor_id.
UNIQUE(event_key) pozwala pominąć dokładne powtórzenia. Każda partia ma
własną transakcję, więc błąd zapisu powoduje wycofanie całej partii.

Klucze i ograniczenia: network_events ma PK event_id, UNIQUE event_key
i FK sensor_id do sensors. CHECK pilnuje zakresu portów, protokołu,
akcji i wartości nieujemnych. alerts ma PK alert_id, unikatową kombinację
(source_ip, rule_name, first_seen) oraz CHECK statusu i liczby zdarzeń.
alert_status_history wskazuje alert przez FK. Trigger
log_alert_status_change zapisuje historię wyłącznie przy zmianie statusu.

Na kopii startowej oba importy dodały 0 wierszy (CSV był już załadowany).
Na kopii z pustą tabelą network_events pierwszy import dodał 896 wierszy,
drugi 0. ROLLBACK przywrócił status OPEN i usunął nowy wpis historii.
Indeks (src_ip, timestamp) umożliwił wyszukanie po adresie i zakresie czasu
oraz sortowanie bez tymczasowego drzewa B. Plan pokazuje strategię odczytu.
