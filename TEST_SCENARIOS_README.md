# UKConnect Customer Support - Test Scenarios

This document provides a comprehensive overview of the 15 test scenarios designed to validate the UKConnect AI Customer Support system across different customer types, communication styles, and use cases.

## 🎯 Overview

The test scenarios cover:
- **Multi-agent orchestration** (Master, Policy, and Ticket agents)
- **Location intelligence** for context-aware booking
- **Various communication styles** (formal business to casual modern)
- **Complex workflows** spanning multiple agent capabilities
- **Real customer data** with proper context preservation

## 🧪 Test Execution

### Quick Test
```bash
python run_test_scenarios.py
```

### Specific Scenario
```bash
python run_test_scenarios.py --session 1    # New customer journey
python run_test_scenarios.py --session 11   # Casual communication
python run_test_scenarios.py --session 15   # Complex booking scenario
```

### All Scenarios (Full Test Suite)
```bash
python run_test_scenarios.py --all
```

### Interactive Testing
```bash
python interactive_test.py
```

## 📋 Test Scenarios Breakdown

### **Formal/Business Sessions (1-10)**
Professional communication style testing core functionality:

#### **Session 1: New Customer Journey**
- **Customer**: James Thompson (CUS001)
- **Focus**: First-time user experience, policy questions, guided booking
- **Tests**: Policy agent knowledge, ticket search, booking flow

#### **Session 2: Refund & Rebooking**
- **Customer**: Sarah Williams (CUS002)  
- **Focus**: Complex refund calculations, rebooking workflows
- **Tests**: Policy agent refund rules, ticket modifications, multi-step processes

#### **Session 3: Complex Queries**
- **Customer**: Michael Davies (CUS003)
- **Focus**: Multi-domain questions requiring both agents
- **Tests**: Agent orchestration, context preservation, complex routing

#### **Session 4: Business Traveler**
- **Customer**: Emily Johnson (CUS004)
- **Focus**: Professional booking requirements, expense management
- **Tests**: Business fare options, receipt generation, corporate policies

#### **Session 5: Problem Resolution**
- **Customer**: Robert Brown (CUS005)
- **Focus**: Issue escalation, customer service recovery
- **Tests**: Error handling, problem-solving workflows, customer satisfaction

#### **Session 6: Frequent Traveler**
- **Customer**: Lisa Wilson (CUS006)
- **Focus**: Advanced user features, loyalty benefits
- **Tests**: Customer history, personalized service, efficiency optimization

#### **Session 7: Budget Travel**
- **Customer**: David Evans (CUS007)
- **Focus**: Cost-conscious booking, fare comparisons
- **Tests**: Price optimization, discount applications, value recommendations

#### **Session 8: Accessibility Needs**
- **Customer**: Jennifer Smith (CUS008)
- **Focus**: Special assistance requirements, accessibility support
- **Tests**: Special services, accommodation booking, compliance features

#### **Session 9: International Visitor**
- **Customer**: Christopher Jones (CUS009)
- **Focus**: Tourist information, simplified explanations
- **Tests**: Clear communication, helpful guidance, cultural sensitivity

#### **Session 10: Comprehensive Test**
- **Customer**: Amanda Taylor (CUS010)
- **Focus**: Full system validation across all features
- **Tests**: Complete workflow coverage, performance validation

### **Casual/Modern Sessions (11-15)**
Modern communication styles with location intelligence:

#### **Session 11: Casual Student** 
- **Customer**: Alex Smith (CUS051) | Location: London Euston
- **Style**: "yo need train london to bham tmrw"
- **Tests**: Informal language processing, location intelligence, student discounts

#### **Session 12: Young Professional**
- **Customer**: Jordan Wilson (CUS052) | Location: London King's Cross  
- **Style**: Mobile-first, emoji usage, abbreviated text
- **Tests**: Modern communication adaptation, professional needs

#### **Session 13: Mobile User**
- **Customer**: Casey Brown (CUS053) | Location: Birmingham New Street
- **Style**: Short messages, autocorrect artifacts, voice-to-text patterns
- **Tests**: Mobile interface optimization, context preservation

#### **Session 14: Urgent Travel**
- **Customer**: Sam Taylor (CUS054) | Location: London King's Cross
- **Style**: High urgency, emotional context, emergency booking
- **Tests**: Priority handling, stress management, rapid resolution

#### **Session 15: Social Style**
- **Customer**: Riley Jones (CUS055) | Location: Glasgow Central
- **Style**: Social media influenced, creative language, generation Z communication
- **Tests**: Cultural adaptation, engagement optimization, personality matching

## 🎯 Location Intelligence Testing

Sessions 11-15 specifically test the location intelligence feature where:
- Customers provide minimal departure context
- System uses customer address to infer departure stations
- Smart defaults reduce booking friction
- Location-aware recommendations improve user experience

**Example Flow:**
```
User: "need train to manchester tomorrow"
System: [Uses CUS051 address] "I can see several options from London Euston to Manchester..."
```

## 📊 Performance Metrics

Each test scenario measures:
- **Response Time**: End-to-end interaction speed
- **Routing Accuracy**: Correct agent selection percentage  
- **Context Preservation**: Information retention across turns
- **Resolution Rate**: Successful task completion
- **Customer Satisfaction**: Communication quality assessment

## 🔄 Test Data Management

### Customer Database
- **15 real customer profiles** with complete address and booking history
- **Location mapping** for intelligent departure station detection
- **Preference profiles** for personalized service testing

### Booking Data
- **Historical transactions** for context-aware recommendations
- **Active bookings** for modification and cancellation testing
- **Fare variations** for pricing optimization validation

## 🚀 Running Specific Test Categories

### Policy-Heavy Tests (Sessions 2, 3, 8, 9)
```bash
python run_test_scenarios.py --session 2 --session 3 --session 8 --session 9
```

### Location Intelligence Tests (Sessions 11-15)
```bash
python run_test_scenarios.py --session 11 --session 12 --session 13 --session 14 --session 15
```

### Business User Tests (Sessions 1, 4, 6, 10)
```bash
python run_test_scenarios.py --session 1 --session 4 --session 6 --session 10
```

## 📈 Expected Results

### Success Criteria
- ✅ **100% routing accuracy** - Queries directed to correct agents
- ✅ **<2 second response time** - Fast interaction speed
- ✅ **Context preservation** - Information retained across conversation
- ✅ **Natural language adaptation** - Appropriate response tone matching
- ✅ **Location intelligence** - Accurate departure station inference

### Validation Points
- Master agent correctly analyzes query intent
- Policy agent retrieves accurate information from knowledge base
- Ticket agent executes database operations successfully
- Response synthesis maintains conversation flow
- Error handling provides graceful fallbacks

## 🐛 Troubleshooting

### Common Issues
1. **API Key Missing**: Ensure `GOOGLE_API_KEY` is set in `.env`
2. **Database Not Found**: Run database initialization first
3. **Import Errors**: Check all dependencies are installed
4. **Timeout Issues**: Verify network connectivity for API calls

### Debug Mode
```bash
python run_test_scenarios.py --session 1 --debug
```

This enables detailed logging for troubleshooting agent interactions and performance analysis.

---

## 📝 Adding New Scenarios

To add new test scenarios:

1. **Define customer profile** in `utils/customer_setup.py`
2. **Create message sequence** in `test_message_scenarios.py` 
3. **Add session mapping** in the scenarios dictionary
4. **Update this documentation** with scenario description

Each scenario should test specific functionality while maintaining realistic customer interaction patterns.