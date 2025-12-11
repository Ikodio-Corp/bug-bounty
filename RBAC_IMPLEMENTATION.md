# Role-Based Access Control (RBAC) Implementation

## Overview
Implementasi lengkap sistem Role-Based Access Control berdasarkan subscription tier pengguna. Sistem ini mengontrol akses ke fitur-fitur premium di dashboard dan aplikasi.

## Architecture

### 1. Subscription Context (`contexts/SubscriptionContext.tsx`)
Context global yang menyimpan informasi user dan tier subscription.

**Tier Levels:**
- **Free**: Rp 0/bulan - Fitur dasar
- **Starter**: Rp 199.000/bulan - Fitur lanjutan
- **Professional**: Rp 450.000/bulan - Fitur premium
- **Enterprise**: Custom - Fitur unlimited

**Features by Tier:**

#### Free Tier
- 5 scans per bulan
- 2 target domains max
- Basic scanner (Nuclei)
- PDF reports
- Community support
- 30 days scan history

#### Starter Tier
- 25 scans per bulan
- 5 target domains max
- Advanced scanners (Nuclei + ZAP)
- PDF + HTML reports
- Email support (24h response)
- Email notifications
- 30 days scan history

#### Professional Tier
- 100 scans per bulan
- Unlimited target domains
- AI Scanner + all tools
- Custom report templates
- API access & webhooks
- Real-time alerts
- Guild & Marketplace access
- Advanced analytics dashboard
- Priority support 24/7
- Scheduled scans
- Slack/Discord integration
- Export data (JSON, CSV, XML)
- Unlimited scan history
- Team collaboration (5 users)

#### Enterprise Tier
- Unlimited scans
- Unlimited domains
- Dedicated security expert
- Custom AI model training
- White-label solution
- SLA 99.9% uptime
- On-premise deployment
- Unlimited team members
- Compliance reports (ISO, PCI-DSS)
- Custom integrations
- SSO & LDAP integration
- Multi-region deployment
- Custom security policies
- Advanced threat intelligence

**Context API:**
```typescript
const {
  user,           // User data with tier info
  tier,           // Current subscription tier
  features,       // Available features object
  isLoading,      // Loading state
  hasFeature,     // Check if feature is available
  canUseScan,     // Check if can run more scans
  canAddDomain,   // Check if can add more domains
  refreshUser     // Refresh user data
} = useSubscription()
```

### 2. Feature Locking Components (`components/FeatureLocked.tsx`)

#### FeatureLocked Component
Wrap fitur yang perlu dibatasi berdasarkan tier.

```typescript
<FeatureLocked
  feature="Performance Analytics"
  requiredTier="professional"
  blur={true}  // Blur content atau opacity
  showUpgrade={true}  // Tampilkan tombol upgrade
>
  <PerformanceChart />
</FeatureLocked>
```

**Properties:**
- `feature`: Nama fitur yang dikunci
- `requiredTier`: Tier minimum yang diperlukan
- `blur`: Boolean untuk blur atau opacity
- `showUpgrade`: Tampilkan tombol upgrade overlay

#### InlineFeatureLocked Component
Badge kecil untuk menandai fitur yang dikunci.

```typescript
<InlineFeatureLocked
  feature="API Access"
  requiredTier="professional"
  compact={true}
/>
```

#### ScanLimitIndicator Component
Menampilkan usage scan bulanan dengan progress bar.

```typescript
<ScanLimitIndicator className="mb-6" />
```

Features:
- Progress bar dengan color coding
- Red: >80% usage
- Amber: 50-80% usage
- Green: <50% usage
- Alert ketika limit tercapai

### 3. Dashboard Integration (`app/dashboard/page.tsx`)

Dashboard menggunakan SubscriptionContext untuk mengatur akses fitur:

```typescript
const { features, isLoading } = useSubscription();

// Advanced Analytics - Locked for Free/Starter
{features.advancedAnalytics ? (
  <PerformanceChart />
) : (
  <FeatureLocked
    feature="Performance Analytics"
    requiredTier="professional"
    blur={true}
  >
    <PerformanceChart />
  </FeatureLocked>
)}

// Real-time Activity - Locked for Free/Starter
{features.realTimeAlerts ? (
  <RefinedLiveActivity />
) : (
  <FeatureLocked
    feature="Real-time Activity Feed"
    requiredTier="professional"
    blur={true}
  >
    <RefinedLiveActivity />
  </FeatureLocked>
)}
```

### 4. Sidebar Navigation (`components/dashboard/Sidebar.tsx`)

Menu sidebar menampilkan locked state untuk fitur yang tidak tersedia:

```typescript
const mainMenu: NavItem[] = [
  { 
    icon: ShoppingBag, 
    label: 'Marketplace', 
    href: '/marketplace',
    requiresFeature: 'marketplaceAccess',
    requiredTier: 'professional'
  },
  { 
    icon: Users, 
    label: 'Guild Center', 
    href: '/guilds',
    requiresFeature: 'guildAccess',
    requiredTier: 'professional'
  },
  // ...
];
```

**Features:**
- Menu item dengan icon Lock untuk fitur terkunci
- Crown icon untuk premium features
- User profile badge menampilkan tier
- Color coding berdasarkan tier level

### 5. Quick Actions (`components/dashboard/RefinedQuickActions.tsx`)

Quick actions button dengan tier restrictions:

```typescript
const actions: Action[] = [
  {
    id: '3',
    label: 'Marketplace',
    description: 'Browse tools & services',
    icon: ShoppingCart,
    href: '/marketplace',
    requiresFeature: 'marketplaceAccess',
    requiredTier: 'professional',
  },
  // ...
];
```

**Behavior:**
- Locked features show lock icon
- Display required tier
- Prevent navigation when locked
- Show scan limit reached for new scan

### 6. Subscription Card (`components/dashboard/SubscriptionCard.tsx`)

Menampilkan informasi tier dan usage:

**Features:**
- Tier badge dengan color coding
- Usage progress bars (scans, domains)
- Active features list
- Upgrade button (except Enterprise)
- Warning alert ketika mendekati limit

**Color Scheme:**
- Free: Gray gradient
- Starter: Blue gradient
- Professional: Amber/Orange gradient
- Enterprise: Purple gradient

### 7. Upgrade Modal

Modal yang muncul ketika user mencoba akses fitur locked:

**Features:**
- Feature name yang dikunci
- Required tier information
- Tier benefits list
- Price display
- Upgrade CTA button
- Cancel option

## Usage Examples

### Example 1: Lock Advanced Analytics
```typescript
import { FeatureLocked } from '@/components/FeatureLocked';

{features.advancedAnalytics ? (
  <AnalyticsChart />
) : (
  <FeatureLocked
    feature="Advanced Analytics"
    requiredTier="professional"
  >
    <AnalyticsChart />
  </FeatureLocked>
)}
```

### Example 2: Check Scan Limit
```typescript
import { useSubscription } from '@/contexts/SubscriptionContext';

const { canUseScan } = useSubscription();

const handleStartScan = () => {
  if (!canUseScan()) {
    alert('Scan limit reached. Please upgrade.');
    return;
  }
  // Start scan logic
};
```

### Example 3: Check Feature Access
```typescript
const { hasFeature } = useSubscription();

if (hasFeature('apiAccess')) {
  // Show API documentation
} else {
  // Show upgrade prompt
}
```

### Example 4: Conditional Rendering
```typescript
{features.guildAccess && (
  <GuildPanel />
)}

{!features.marketplaceAccess && (
  <InlineFeatureLocked
    feature="Marketplace"
    requiredTier="professional"
  />
)}
```

## Feature Matrix

| Feature | Free | Starter | Professional | Enterprise |
|---------|------|---------|--------------|------------|
| Scans/month | 5 | 25 | 100 | Unlimited |
| Target Domains | 2 | 5 | Unlimited | Unlimited |
| Basic Scanner |  |  |  |  |
| Advanced Scanner |  |  |  |  |
| AI Scanner |  |  |  |  |
| API Access |  |  |  |  |
| Marketplace |  |  |  |  |
| Guild Access |  |  |  |  |
| Real-time Alerts |  |  |  |  |
| Advanced Analytics |  |  |  |  |
| Team Collaboration |  |  | 5 users | Unlimited |
| White-label |  |  |  |  |
| Dedicated Expert |  |  |  |  |
| SLA 99.9% |  |  |  |  |

## Backend Integration

For production, replace mock data in `SubscriptionContext.tsx`:

```typescript
const loadUser = async () => {
  setIsLoading(true);
  try {
    // Replace with actual API call
    const response = await fetch('/api/user/subscription');
    const data = await response.json();
    
    setUser({
      id: data.id,
      email: data.email,
      fullName: data.full_name,
      tier: data.subscription_tier,
      subscriptionStartDate: data.subscription_start,
      subscriptionEndDate: data.subscription_end,
      scansUsedThisMonth: data.scans_used,
      targetDomainsCount: data.domains_count
    });
  } catch (error) {
    console.error('Failed to load user:', error);
  } finally {
    setIsLoading(false);
  }
};
```

## Testing Different Tiers

To test different tiers, change the mock tier in `SubscriptionContext.tsx`:

```typescript
const mockUser: User = {
  // ...
  tier: 'free',        // Change to: 'free', 'starter', 'professional', 'enterprise'
  // ...
}
```

## Upgrade Flow

1. User clicks "Upgrade" button
2. Redirected to pricing page (`/`)
3. Select desired tier
4. Navigate through: Register †’ Terms †’ User Data †’ Payment
5. After successful payment, tier updated
6. Dashboard reflects new permissions immediately

## Security Considerations

1. **Client-side validation only**: Current implementation is UI-only
2. **Backend enforcement required**: Always validate permissions on backend
3. **API endpoints**: Must check user tier before allowing actions
4. **Token/Session**: Store tier in JWT or session
5. **Real-time updates**: Implement websocket for tier changes

## Files Created/Modified

### Created:
1. `contexts/SubscriptionContext.tsx` - Global subscription state
2. `components/FeatureLocked.tsx` - Feature locking components

### Modified:
1. `app/layout.tsx` - Added SubscriptionProvider wrapper
2. `app/dashboard/page.tsx` - Added feature restrictions
3. `components/dashboard/Sidebar.tsx` - Added locked menu items
4. `components/dashboard/RefinedQuickActions.tsx` - Added action restrictions
5. `components/dashboard/SubscriptionCard.tsx` - Rebuilt with tier info

## Summary

Implementasi RBAC lengkap dengan:
-  4 tier subscription (Free, Starter, Professional, Enterprise)
-  Feature matrix untuk setiap tier
-  Context API untuk state management
-  Feature locking components (blur/opacity)
-  Upgrade modals dengan pricing info
-  Dashboard restrictions
-  Sidebar menu restrictions
-  Quick actions restrictions
-  Usage indicators dan progress bars
-  Scan limit enforcement
-  Domain limit enforcement
-  Visual tier badges
-  Color coding by tier
-  Responsive design
-  Smooth animations

Sistem siap diintegrasikan dengan backend untuk enforcement permissions di server-side.
