#!/usr/bin/env python3
"""
Demo Script für die Next Opening Calculator Status Logic
Zeigt die Funktionalität der intelligenten Öffnungszeit-Berechnung

Dieses Demo-Script demonstriert:
- Aktuelle Status-Berechnung
- Next Opening Logic
- Thai Holiday Integration  
- Mehrsprachige Ausgaben
- Edge Case Handling
"""

import sys
import os
sys.path.append('.')

from datetime import date, datetime, time
from app.services.next_opening_calculator import (
    NextOpeningCalculator, 
    get_smart_status,
    get_today_remaining_slots,
    is_open_now,
    get_next_opening_info
)
from app.services.exception_engine import (
    ThaiHolidayCalculator,
    ExceptionEngine,
    get_next_thai_holiday,
    get_thai_holidays_this_month
)


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print section header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def demo_bangkok_time():
    """Demo Bangkok Timezone Handling"""
    print_header("🇹🇭 BANGKOK TIMEZONE DEMO")
    
    current_time = NextOpeningCalculator.get_current_bangkok_time()
    print(f"Current Bangkok Time: {current_time}")
    print(f"Date: {current_time.date()}")
    print(f"Time: {current_time.time()}")
    print(f"Timezone: {current_time.tzinfo}")
    print(f"Weekday: {current_time.strftime('%A')}")


def demo_thai_holidays():
    """Demo Thai Holiday System"""
    print_header("🏮 THAI HOLIDAYS DEMO")
    
    # Get holidays for current year
    current_year = datetime.now().year
    holidays = ThaiHolidayCalculator.get_fixed_holidays(current_year)
    
    print(f"Found {len(holidays)} Thai holidays for {current_year}")
    
    print_section("Major National Holidays")
    national_holidays = [h for h in holidays if h.type.value == 'NATIONAL_HOLIDAY']
    for holiday in national_holidays[:5]:  # Show first 5
        print(f"📅 {holiday.date} - {holiday.name_th}")
        print(f"   🇩🇪 {holiday.name_de}")
        print(f"   🇺🇸 {holiday.name_en}")
        if holiday.description_th:
            print(f"   📝 {holiday.description_th}")
        print()
    
    print_section("Royal Holidays")
    royal_holidays = [h for h in holidays if h.type.value == 'ROYAL_HOLIDAY']
    for holiday in royal_holidays[:3]:  # Show first 3
        print(f"👑 {holiday.date} - {holiday.name_th}")
        print(f"   🇩🇪 {holiday.name_de}")
        print()
    
    print_section("Buddhist Holidays")  
    buddhist_holidays = [h for h in holidays if h.type.value == 'BUDDHIST_HOLIDAY']
    for holiday in buddhist_holidays[:3]:  # Show first 3
        print(f"🙏 {holiday.date} - {holiday.name_th}")
        print(f"   🇩🇪 {holiday.name_de}")
        print()


def demo_holiday_detection():
    """Demo Holiday Detection Logic"""
    print_header("🔍 HOLIDAY DETECTION DEMO")
    
    # Test specific dates
    test_dates = [
        date(2025, 1, 1),   # New Year
        date(2025, 4, 13),  # Songkran
        date(2025, 5, 1),   # Labour Day
        date(2025, 12, 31), # New Year's Eve
        date(2025, 3, 15),  # Regular day
    ]
    
    for test_date in test_dates:
        holiday = ExceptionEngine.is_thai_holiday(test_date)
        if holiday:
            print(f"✅ {test_date} IS a Thai holiday:")
            print(f"   🇹🇭 {holiday.name_th}")
            print(f"   🇩🇪 {holiday.name_de}")
            print(f"   📂 Type: {holiday.type.value}")
            print(f"   🏢 Affects Business: {holiday.affects_business}")
        else:
            print(f"❌ {test_date} is NOT a Thai holiday")
        print()


def demo_next_opening_logic():
    """Demo Next Opening Calculation"""
    print_header("⏰ NEXT OPENING LOGIC DEMO")
    
    try:
        # Get today status (mock data since we don't have a real database)
        print_section("Today's Status Analysis")
        print("⚠️  Note: This demo uses mock data since no database is connected")
        print()
        
        # Show what the calculator would do
        bangkok_time = NextOpeningCalculator.get_current_bangkok_time()
        print(f"Current Bangkok Time: {bangkok_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Day of Week: {bangkok_time.strftime('%A')}")
        print(f"Is Weekend: {bangkok_time.weekday() >= 5}")
        
        # Mock scenario demonstrations
        print_section("Mock Scenarios")
        
        scenarios = [
            {
                'name': 'Currently Open (10:30 on Friday)',
                'time': '10:30',
                'day': 'Friday',
                'status': 'open',
                'closes_at': '12:00',
                'next_slot': '13:00-16:00'
            },
            {
                'name': 'Opens Soon (08:00, opens at 08:30)',
                'time': '08:00', 
                'day': 'Monday',
                'status': 'closed',
                'opens_in': '30 minutes',
                'next_slot': '08:30-12:00'
            },
            {
                'name': 'On Vacation (August 22-30)',
                'time': '10:00',
                'day': 'Friday',
                'status': 'vacation',
                'reason': 'Sommerurlaub',
                'next_opening': '2025-09-02 08:30'
            },
            {
                'name': 'Weekend (Sunday)',
                'time': '14:00',
                'day': 'Sunday', 
                'status': 'weekend',
                'next_opening': 'Monday 08:30'
            }
        ]
        
        for scenario in scenarios:
            print(f"🎭 Scenario: {scenario['name']}")
            print(f"   📅 Time: {scenario['day']} {scenario['time']}")
            
            if scenario['status'] == 'open':
                print(f"   ✅ Status: Currently OPEN")
                print(f"   ⏰ Closes at: {scenario['closes_at']}")
                print(f"   📋 Next slot: {scenario['next_slot']}")
            elif scenario['status'] == 'closed':
                print(f"   🕐 Status: CLOSED - Opens soon")
                print(f"   ⏰ Opens in: {scenario['opens_in']}")
                print(f"   📋 Next slot: {scenario['next_slot']}")
            elif scenario['status'] == 'vacation':
                print(f"   🏖️ Status: ON VACATION")
                print(f"   📝 Reason: {scenario['reason']}")
                print(f"   ⏰ Next opening: {scenario['next_opening']}")
            elif scenario['status'] == 'weekend':
                print(f"   📅 Status: WEEKEND")
                print(f"   ⏰ Next opening: {scenario['next_opening']}")
            print()
        
    except Exception as e:
        print(f"⚠️  Demo limited due to missing database connection: {e}")
        print("   In production, this would show real-time status calculations")


def demo_multilingual_messages():
    """Demo Multilingual Status Messages"""
    print_header("🌐 MULTILINGUAL MESSAGES DEMO")
    
    # Mock status messages in different languages
    mock_messages = {
        'currently_open': {
            'th': 'เปิดให้บริการอยู่ - ปิดเวลา 16:00',
            'de': 'Geöffnet - Schließt um 16:00', 
            'en': 'Open now - Closes at 16:00'
        },
        'opens_soon': {
            'th': 'เปิดในอีก 30 นาที (08:30)',
            'de': 'Öffnet in 30 Minuten (08:30)',
            'en': 'Opens in 30 minutes (08:30)'
        },
        'on_vacation': {
            'th': 'ปิดทำการ: ลาพักร้อน (22.08 - 30.08)',
            'de': 'Geschlossen: Urlaub (22.08 - 30.08)',
            'en': 'Closed: Vacation (22.08 - 30.08)'
        },
        'thai_holiday': {
            'th': 'ปิดทำการ: วันขึ้นปีใหม่',
            'de': 'Geschlossen: Neujahr',
            'en': 'Closed: New Year\'s Day'
        }
    }
    
    for scenario, messages in mock_messages.items():
        print(f"📱 Scenario: {scenario.replace('_', ' ').title()}")
        print(f"   🇹🇭 Thai: {messages['th']}")
        print(f"   🇩🇪 German: {messages['de']}")
        print(f"   🇺🇸 English: {messages['en']}")
        print()


def demo_template_functions():
    """Demo Template Helper Functions"""
    print_header("📄 TEMPLATE FUNCTIONS DEMO")
    
    print_section("Next Thai Holiday")
    try:
        next_holiday = get_next_thai_holiday(lang='th')
        if next_holiday:
            print(f"📅 Next Thai Holiday: {next_holiday['name']}")
            print(f"   📆 Date: {next_holiday['date']}")
            print(f"   ⏳ Days until: {next_holiday['days_until']}")
            print(f"   🏷️ Type: {next_holiday['type']}")
        else:
            print("❌ No Thai holidays found in next 365 days")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print_section("This Month's Thai Holidays")
    try:
        holidays_this_month = get_thai_holidays_this_month(lang='th')
        if holidays_this_month:
            print(f"Found {len(holidays_this_month)} holidays this month:")
            for holiday in holidays_this_month:
                print(f"   📅 {holiday['date']} - {holiday['name']}")
        else:
            print("❌ No Thai holidays this month")
    except Exception as e:
        print(f"⚠️  Error: {e}")


def demo_cache_performance():
    """Demo Cache Performance"""
    print_header("⚡ CACHE PERFORMANCE DEMO")
    
    import time
    
    print("Testing cache mechanism...")
    
    # Clear cache first
    NextOpeningCalculator._cache.clear()
    print(f"Cache cleared. Size: {len(NextOpeningCalculator._cache)}")
    
    # Simulate cache operations
    print("\n🔄 Simulating repeated calls...")
    for i in range(3):
        start_time = time.time()
        
        # This would normally cache results
        bangkok_time = NextOpeningCalculator.get_current_bangkok_time()
        
        end_time = time.time()
        print(f"   Call {i+1}: {(end_time - start_time)*1000:.2f}ms - {bangkok_time.strftime('%H:%M:%S')}")
    
    print(f"\nCache size after operations: {len(NextOpeningCalculator._cache)}")
    print(f"Cache timeout: {NextOpeningCalculator._cache_timeout}")


def demo_edge_cases():
    """Demo Edge Cases"""
    print_header("🎯 EDGE CASES DEMO")
    
    print_section("Timezone Edge Cases")
    
    # Test different times of day
    edge_times = [
        "00:00 (Midnight)",
        "06:00 (Early Morning)", 
        "12:00 (Noon)",
        "18:00 (Evening)",
        "23:59 (Almost Midnight)"
    ]
    
    bangkok_time = NextOpeningCalculator.get_current_bangkok_time()
    print(f"Current Bangkok time: {bangkok_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    for edge_time in edge_times:
        print(f"   ⏰ {edge_time}")
    
    print_section("Date Edge Cases")
    date_edges = [
        "Year transition (2024 -> 2025)",
        "Month transition (January -> February)",
        "Leap year handling (2024 vs 2025)",
        "Weekend transitions (Friday -> Monday)",
        "Holiday periods (Songkran week)"
    ]
    
    for edge_case in date_edges:
        print(f"   📅 {edge_case}")
    
    print("\n📝 Note: In production, these edge cases are handled by:")
    print("   - Proper timezone conversion (pytz)")  
    print("   - Database queries for exact schedules")
    print("   - Status validation with date ranges")
    print("   - Cache invalidation at proper intervals")


def main():
    """Main demo function"""
    print("🇹🇭 QR-Info-Portal: Next Opening Calculator Demo")
    print("=" * 60)
    print("Demonstrating intelligent opening time calculation for Thai laboratory")
    
    try:
        demo_bangkok_time()
        demo_thai_holidays()
        demo_holiday_detection()
        demo_next_opening_logic()
        demo_multilingual_messages()
        demo_template_functions()
        demo_cache_performance()
        demo_edge_cases()
        
        print_header("✅ DEMO COMPLETE")
        print("The Next Opening Calculator system includes:")
        print("• 🕐 Real-time Bangkok timezone handling")
        print("• 🏮 18+ Thai holidays with multilingual names")
        print("• 🔍 Intelligent status detection")
        print("• ⏰ Smart opening time calculation")
        print("• 🌐 Full Thai/German/English support")
        print("• ⚡ 15-minute caching for performance")
        print("• 🎯 Comprehensive edge case handling")
        print("• 📱 Template functions for easy integration")
        
        print(f"\n📊 System Statistics:")
        print(f"   Thai holidays: {len(ThaiHolidayCalculator.get_fixed_holidays(2025))}")
        print(f"   Supported languages: 3 (th, de, en)")
        print(f"   Cache timeout: {NextOpeningCalculator._cache_timeout}")
        print(f"   Max lookahead days: {NextOpeningCalculator.MAX_LOOKAHEAD_DAYS}")
        
    except Exception as e:
        print(f"\n❌ Demo Error: {e}")
        print("This is expected if database is not connected.")
        print("The system is designed for production use with SQLite/PostgreSQL.")


if __name__ == "__main__":
    main()