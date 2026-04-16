import * as sqlite3 from 'sqlite3';
import * as path from 'path';
import * as os from 'os';
import * as fs from 'fs';
import * as https from 'https';
import * as http from 'http';

export interface Property {
  id: string;
  source: string; // 'zillow', 'realtor', 'simulated'
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    full: string;
  };
  price: number;
  priceHistory?: Array<{
    date: string;
    price: number;
    event: string; // 'listed', 'price_change', 'sold', etc.
  }>;
  details: {
    bedrooms: number;
    bathrooms: number;
    sqft: number;
    lotSize?: number;
    yearBuilt?: number;
    propertyType: 'house' | 'condo' | 'townhouse' | 'multi_family' | 'land';
  };
  listing: {
    status: 'active' | 'pending' | 'sold' | 'off_market';
    listedDate: string;
    mlsNumber?: string;
    daysOnMarket: number;
  };
  photos?: string[];
  description?: string;
  features?: string[];
  url?: string;
  agent?: {
    name: string;
    phone?: string;
    email?: string;
    company?: string;
  };
}

export interface PropertySearchCriteria {
  location: string; // City, state, or zip
  minPrice?: number;
  maxPrice?: number;
  minBedrooms?: number;
  maxBedrooms?: number;
  minBathrooms?: number;
  maxBathrooms?: number;
  minSqft?: number;
  maxSqft?: number;
  propertyTypes?: Array<'house' | 'condo' | 'townhouse' | 'multi_family' | 'land'>;
  status?: 'active' | 'pending' | 'sold' | 'all';
  keywords?: string[];
}

export interface SavedSearch {
  id?: number;
  name: string;
  criteria: PropertySearchCriteria;
  alertEnabled: boolean;
  lastCheckedAt?: string;
  createdAt: string;
}

export interface PriceChange {
  propertyId: string;
  oldPrice: number;
  newPrice: number;
  changeAmount: number;
  changePercent: number;
  detectedAt: string;
}

export interface PropertyAlert {
  id?: number;
  searchId: number;
  propertyId: string;
  alertType: 'new_listing' | 'price_drop' | 'price_increase' | 'status_change' | 'back_on_market';
  message: string;
  propertyData: Property;
  oldPrice?: number;
  newPrice?: number;
  isRead: boolean;
  createdAt: string;
}

export interface PropertySearchResults {
  criteria: PropertySearchCriteria;
  properties: Property[];
  totalResults: number;
  fromCache: boolean;
  searchTime: number;
}

// Database record interfaces (snake_case)
interface SavedSearchRecord {
  id: number;
  name: string;
  location: string;
  min_price?: number;
  max_price?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  min_bathrooms?: number;
  max_bathrooms?: number;
  min_sqft?: number;
  max_sqft?: number;
  property_types?: string;
  status: string;
  keywords?: string;
  alert_enabled: number;
  last_checked_at?: string;
  created_at: string;
}

interface PropertyRecord {
  id: number;
  property_id: string;
  source: string;
  address_full: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  lot_size?: number;
  year_built?: number;
  property_type: string;
  status: string;
  listed_date: string;
  days_on_market: number;
  description?: string;
  features?: string;
  url?: string;
  photos?: string;
  agent_name?: string;
  agent_phone?: string;
  agent_email?: string;
  agent_company?: string;
  last_seen_at: string;
  created_at: string;
}

interface PriceHistoryRecord {
  id: number;
  property_id: string;
  price: number;
  event: string;
  recorded_at: string;
}

interface AlertRecord {
  id: number;
  search_id: number;
  property_id: string;
  alert_type: string;
  message: string;
  property_data: string;
  old_price?: number;
  new_price?: number;
  is_read: number;
  created_at: string;
}

// Sample property data for simulated mode
const SAMPLE_PROPERTIES: Property[] = [
  {
    id: 'prop-001',
    source: 'simulated',
    address: {
      street: '123 Main Street',
      city: 'Austin',
      state: 'TX',
      zipCode: '78701',
      full: '123 Main Street, Austin, TX 78701'
    },
    price: 450000,
    details: {
      bedrooms: 3,
      bathrooms: 2,
      sqft: 1850,
      lotSize: 6500,
      yearBuilt: 2010,
      propertyType: 'house'
    },
    listing: {
      status: 'active',
      listedDate: '2026-01-15',
      daysOnMarket: 26,
      mlsNumber: 'MLS-123456'
    },
    features: ['Garage', 'Pool', 'Fireplace', 'Hardwood Floors'],
    description: 'Beautiful 3-bedroom home in central Austin with modern updates.',
    url: 'https://example.com/prop-001'
  },
  {
    id: 'prop-002',
    source: 'simulated',
    address: {
      street: '456 Oak Avenue',
      city: 'Austin',
      state: 'TX',
      zipCode: '78702',
      full: '456 Oak Avenue, Austin, TX 78702'
    },
    price: 325000,
    details: {
      bedrooms: 2,
      bathrooms: 2,
      sqft: 1200,
      yearBuilt: 2005,
      propertyType: 'condo'
    },
    listing: {
      status: 'active',
      listedDate: '2026-02-01',
      daysOnMarket: 9,
      mlsNumber: 'MLS-234567'
    },
    features: ['Gym', 'Pool Access', 'Balcony'],
    description: 'Modern condo with downtown views.',
    url: 'https://example.com/prop-002'
  },
  {
    id: 'prop-003',
    source: 'simulated',
    address: {
      street: '789 Pine Road',
      city: 'Dallas',
      state: 'TX',
      zipCode: '75201',
      full: '789 Pine Road, Dallas, TX 75201'
    },
    price: 675000,
    details: {
      bedrooms: 4,
      bathrooms: 3,
      sqft: 2800,
      lotSize: 8500,
      yearBuilt: 2015,
      propertyType: 'house'
    },
    listing: {
      status: 'active',
      listedDate: '2026-01-20',
      daysOnMarket: 21,
      mlsNumber: 'MLS-345678'
    },
    features: ['Swimming Pool', 'Large Yard', 'Smart Home', 'Chef Kitchen'],
    description: 'Spacious family home with premium finishes.',
    url: 'https://example.com/prop-003'
  },
  {
    id: 'prop-004',
    source: 'simulated',
    address: {
      street: '321 Elm Street',
      city: 'Houston',
      state: 'TX',
      zipCode: '77001',
      full: '321 Elm Street, Houston, TX 77001'
    },
    price: 295000,
    details: {
      bedrooms: 3,
      bathrooms: 2,
      sqft: 1500,
      lotSize: 5500,
      yearBuilt: 1995,
      propertyType: 'house'
    },
    listing: {
      status: 'pending',
      listedDate: '2026-01-10',
      daysOnMarket: 31,
      mlsNumber: 'MLS-456789'
    },
    features: ['Updated Kitchen', 'New Roof', 'Large Driveway'],
    description: 'Well-maintained home in established neighborhood.',
    url: 'https://example.com/prop-004'
  },
  {
    id: 'prop-005',
    source: 'simulated',
    address: {
      street: '555 Highland Ave',
      city: 'Austin',
      state: 'TX',
      zipCode: '78703',
      full: '555 Highland Ave, Austin, TX 78703'
    },
    price: 850000,
    details: {
      bedrooms: 4,
      bathrooms: 3.5,
      sqft: 3200,
      lotSize: 10000,
      yearBuilt: 2018,
      propertyType: 'house'
    },
    listing: {
      status: 'active',
      listedDate: '2026-02-05',
      daysOnMarket: 5,
      mlsNumber: 'MLS-567890'
    },
    features: ['Mountain Views', 'Gourmet Kitchen', 'Wine Cellar', '3-Car Garage'],
    description: 'Luxury home with stunning views and premium amenities.',
    url: 'https://example.com/prop-005'
  }
];

export class PropertyAlertsSkill {
  private db: sqlite3.Database | null = null;
  private dbPath: string;
  private enableCache: boolean;
  private zillowApiKey: string | null;
  private initPromise: Promise<void> | null = null;

  constructor(options: { enableCache?: boolean; dbPath?: string } = {}) {
    this.enableCache = options.enableCache ?? true;
    this.dbPath = options.dbPath || path.join(os.homedir(), '.openclaw', 'skills', 'property-alerts', 'data.db');
    this.zillowApiKey = process.env.ZILLOW_API_KEY || null;

    if (this.enableCache) {
      this.initPromise = this.initializeDatabase();
    }
  }

  private async initializeDatabase(): Promise<void> {
    const dir = path.dirname(this.dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    return new Promise((resolve, reject) => {
      this.db = new (sqlite3 as any).Database(this.dbPath, (err: Error | null) => {
        if (err) {
          reject(err);
          return;
        }
        this.createTables().then(resolve).catch(reject);
      });
    });
  }

  private async createTables(): Promise<void> {
    if (!this.db) return;

    const sql = `
      CREATE TABLE IF NOT EXISTS saved_searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        min_price INTEGER,
        max_price INTEGER,
        min_bedrooms INTEGER,
        max_bedrooms INTEGER,
        min_bathrooms REAL,
        max_bathrooms REAL,
        min_sqft INTEGER,
        max_sqft INTEGER,
        property_types TEXT,
        status TEXT DEFAULT 'active',
        keywords TEXT,
        alert_enabled INTEGER DEFAULT 1,
        last_checked_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,
        address_full TEXT NOT NULL,
        street TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        zip_code TEXT NOT NULL,
        price INTEGER NOT NULL,
        bedrooms INTEGER,
        bathrooms REAL,
        sqft INTEGER,
        lot_size INTEGER,
        year_built INTEGER,
        property_type TEXT,
        status TEXT NOT NULL,
        listed_date TEXT,
        days_on_market INTEGER,
        description TEXT,
        features TEXT,
        url TEXT,
        photos TEXT,
        agent_name TEXT,
        agent_phone TEXT,
        agent_email TEXT,
        agent_company TEXT,
        last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id TEXT NOT NULL,
        price INTEGER NOT NULL,
        event TEXT NOT NULL,
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties(property_id)
      );

      CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        property_id TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        message TEXT NOT NULL,
        property_data TEXT NOT NULL,
        old_price INTEGER,
        new_price INTEGER,
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (search_id) REFERENCES saved_searches(id)
      );

      CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(city, state);
      CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
      CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
      CREATE INDEX IF NOT EXISTS idx_price_history_property ON price_history(property_id);
      CREATE INDEX IF NOT EXISTS idx_alerts_search ON alerts(search_id);
      CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(is_read);
    `;

    return new Promise((resolve, reject) => {
      this.db!.exec(sql, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  private async waitForInit(): Promise<void> {
    if (this.initPromise) {
      await this.initPromise;
    }
  }

  async searchProperties(criteria: PropertySearchCriteria): Promise<PropertySearchResults> {
    const startTime = Date.now();
    await this.waitForInit();

    let results: Property[];

    if (this.zillowApiKey) {
      results = await this.searchWithZillow(criteria);
    } else {
      results = await this.searchSimulated(criteria);
    }

    // Cache the results
    if (this.enableCache) {
      await this.cacheProperties(results);
    }

    return {
      criteria,
      properties: results,
      totalResults: results.length,
      fromCache: false,
      searchTime: Date.now() - startTime
    };
  }

  private async searchWithZillow(criteria: PropertySearchCriteria): Promise<Property[]> {
    // Placeholder for Zillow API integration
    // In production, this would make actual API calls
    return this.searchSimulated(criteria);
  }

  private async searchSimulated(criteria: PropertySearchCriteria): Promise<Property[]> {
    let results = [...SAMPLE_PROPERTIES];

    // Filter by location
    if (criteria.location) {
      const loc = criteria.location.toLowerCase();
      results = results.filter(p => 
        p.address.city.toLowerCase().includes(loc) ||
        p.address.state.toLowerCase().includes(loc) ||
        p.address.zipCode.includes(loc)
      );
    }

    // Filter by price
    if (criteria.minPrice !== undefined) {
      results = results.filter(p => p.price >= criteria.minPrice!);
    }
    if (criteria.maxPrice !== undefined) {
      results = results.filter(p => p.price <= criteria.maxPrice!);
    }

    // Filter by bedrooms
    if (criteria.minBedrooms !== undefined) {
      results = results.filter(p => p.details.bedrooms >= criteria.minBedrooms!);
    }
    if (criteria.maxBedrooms !== undefined) {
      results = results.filter(p => p.details.bedrooms <= criteria.maxBedrooms!);
    }

    // Filter by bathrooms
    if (criteria.minBathrooms !== undefined) {
      results = results.filter(p => p.details.bathrooms >= criteria.minBathrooms!);
    }
    if (criteria.maxBathrooms !== undefined) {
      results = results.filter(p => p.details.bathrooms <= criteria.maxBathrooms!);
    }

    // Filter by square footage
    if (criteria.minSqft !== undefined) {
      results = results.filter(p => p.details.sqft >= criteria.minSqft!);
    }
    if (criteria.maxSqft !== undefined) {
      results = results.filter(p => p.details.sqft <= criteria.maxSqft!);
    }

    // Filter by property type
    if (criteria.propertyTypes && criteria.propertyTypes.length > 0) {
      results = results.filter(p => criteria.propertyTypes!.includes(p.details.propertyType));
    }

    // Filter by status
    if (criteria.status && criteria.status !== 'all') {
      results = results.filter(p => p.listing.status === criteria.status);
    }

    // Filter by keywords
    if (criteria.keywords && criteria.keywords.length > 0) {
      results = results.filter(p => {
        const text = `${p.description || ''} ${(p.features || []).join(' ')}`.toLowerCase();
        return criteria.keywords!.some(kw => text.includes(kw.toLowerCase()));
      });
    }

    return results;
  }

  private async cacheProperties(properties: Property[]): Promise<void> {
    if (!this.db) return;

    for (const prop of properties) {
      const existing = await this.getPropertyById(prop.id);
      
      if (!existing) {
        // New property - insert
        await this.insertProperty(prop);
        await this.insertPriceHistory(prop.id, prop.price, 'listed');
      } else if (existing.price !== prop.price) {
        // Price changed - update
        await this.updatePropertyPrice(prop.id, prop.price);
        await this.insertPriceHistory(prop.id, prop.price, 'price_change');
      } else {
        // Just update last_seen
        await this.updatePropertyLastSeen(prop.id);
      }
    }
  }

  private async getPropertyById(propertyId: string): Promise<PropertyRecord | undefined> {
    if (!this.db) return undefined;

    return new Promise((resolve, reject) => {
      this.db!.get(
        'SELECT * FROM properties WHERE property_id = ?',
        [propertyId],
        (err, row: PropertyRecord | undefined) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  private async insertProperty(prop: Property): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        `INSERT INTO properties 
         (property_id, source, address_full, street, city, state, zip_code, price,
          bedrooms, bathrooms, sqft, lot_size, year_built, property_type, status,
          listed_date, days_on_market, description, features, url, photos,
          agent_name, agent_phone, agent_email, agent_company)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          prop.id, prop.source, prop.address.full, prop.address.street, prop.address.city,
          prop.address.state, prop.address.zipCode, prop.price, prop.details.bedrooms,
          prop.details.bathrooms, prop.details.sqft, prop.details.lotSize || null,
          prop.details.yearBuilt || null, prop.details.propertyType, prop.listing.status,
          prop.listing.listedDate, prop.listing.daysOnMarket, prop.description || null,
          prop.features ? JSON.stringify(prop.features) : null,
          prop.url || null,
          prop.photos ? JSON.stringify(prop.photos) : null,
          prop.agent?.name || null, prop.agent?.phone || null, prop.agent?.email || null,
          prop.agent?.company || null
        ],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  private async updatePropertyPrice(propertyId: string, newPrice: number): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'UPDATE properties SET price = ?, last_seen_at = CURRENT_TIMESTAMP WHERE property_id = ?',
        [newPrice, propertyId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  private async updatePropertyLastSeen(propertyId: string): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'UPDATE properties SET last_seen_at = CURRENT_TIMESTAMP WHERE property_id = ?',
        [propertyId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  private async insertPriceHistory(propertyId: string, price: number, event: string): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'INSERT INTO price_history (property_id, price, event) VALUES (?, ?, ?)',
        [propertyId, price, event],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  // Saved Searches
  async saveSearch(name: string, criteria: PropertySearchCriteria, alertEnabled: boolean = true): Promise<SavedSearch> {
    await this.waitForInit();
    if (!this.db) throw new Error('Database not initialized');

    return new Promise((resolve, reject) => {
      this.db!.run(
        `INSERT INTO saved_searches 
         (name, location, min_price, max_price, min_bedrooms, max_bedrooms,
          min_bathrooms, max_bathrooms, min_sqft, max_sqft, property_types,
          status, keywords, alert_enabled)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          name, criteria.location, criteria.minPrice || null, criteria.maxPrice || null,
          criteria.minBedrooms || null, criteria.maxBedrooms || null,
          criteria.minBathrooms || null, criteria.maxBathrooms || null,
          criteria.minSqft || null, criteria.maxSqft || null,
          criteria.propertyTypes ? JSON.stringify(criteria.propertyTypes) : null,
          criteria.status || 'active',
          criteria.keywords ? JSON.stringify(criteria.keywords) : null,
          alertEnabled ? 1 : 0
        ],
        function(this: sqlite3.RunResult, err: Error | null) {
          if (err) {
            reject(err);
            return;
          }
          resolve({
            id: this.lastID,
            name,
            criteria,
            alertEnabled,
            createdAt: new Date().toISOString()
          });
        }
      );
    });
  }

  async getSavedSearches(): Promise<SavedSearch[]> {
    await this.waitForInit();
    if (!this.db) return [];

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM saved_searches ORDER BY created_at DESC',
        (err, rows: SavedSearchRecord[]) => {
          if (err) {
            reject(err);
            return;
          }
          resolve(rows.map(row => this.mapSavedSearchRecord(row)));
        }
      );
    });
  }

  async getSavedSearch(id: number): Promise<SavedSearch | null> {
    await this.waitForInit();
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      this.db!.get(
        'SELECT * FROM saved_searches WHERE id = ?',
        [id],
        (err, row: SavedSearchRecord | undefined) => {
          if (err) {
            reject(err);
            return;
          }
          resolve(row ? this.mapSavedSearchRecord(row) : null);
        }
      );
    });
  }

  private mapSavedSearchRecord(row: SavedSearchRecord): SavedSearch {
    return {
      id: row.id,
      name: row.name,
      criteria: {
        location: row.location,
        minPrice: row.min_price || undefined,
        maxPrice: row.max_price || undefined,
        minBedrooms: row.min_bedrooms || undefined,
        maxBedrooms: row.max_bedrooms || undefined,
        minBathrooms: row.min_bathrooms || undefined,
        maxBathrooms: row.max_bathrooms || undefined,
        minSqft: row.min_sqft || undefined,
        maxSqft: row.max_sqft || undefined,
        propertyTypes: row.property_types ? JSON.parse(row.property_types) : undefined,
        status: row.status as any,
        keywords: row.keywords ? JSON.parse(row.keywords) : undefined
      },
      alertEnabled: row.alert_enabled === 1,
      lastCheckedAt: row.last_checked_at || undefined,
      createdAt: row.created_at
    };
  }

  async deleteSavedSearch(id: number): Promise<boolean> {
    await this.waitForInit();
    if (!this.db) return false;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'DELETE FROM saved_searches WHERE id = ?',
        [id],
        function(this: sqlite3.RunResult, err: Error | null) {
          if (err) {
            reject(err);
            return;
          }
          resolve(this.changes > 0);
        }
      );
    });
  }

  // Alert checking
  async checkForAlerts(searchId?: number): Promise<PropertyAlert[]> {
    await this.waitForInit();
    if (!this.db) return [];

    const alerts: PropertyAlert[] = [];
    const searches = searchId 
      ? [await this.getSavedSearch(searchId)].filter(Boolean) as SavedSearch[]
      : await this.getSavedSearches().then(s => s.filter(srch => srch.alertEnabled));

    for (const search of searches) {
      const currentResults = await this.searchProperties(search.criteria);
      const searchAlerts = await this.detectChanges(search.id!, currentResults.properties);
      
      for (const alert of searchAlerts) {
        await this.saveAlert(alert);
        alerts.push(alert);
      }

      // Update last checked
      await this.updateLastChecked(search.id!);
    }

    return alerts;
  }

  private async detectChanges(searchId: number, currentProperties: Property[]): Promise<PropertyAlert[]> {
    if (!this.db) return [];

    const alerts: PropertyAlert[] = [];

    for (const prop of currentProperties) {
      const existing = await this.getPropertyById(prop.id);

      if (!existing) {
        // New listing
        alerts.push({
          searchId,
          propertyId: prop.id,
          alertType: 'new_listing',
          message: `New listing: ${prop.address.full} - $${prop.price.toLocaleString()}`,
          propertyData: prop,
          newPrice: prop.price,
          isRead: false,
          createdAt: new Date().toISOString()
        });
      } else if (existing.price > prop.price) {
        // Price drop
        alerts.push({
          searchId,
          propertyId: prop.id,
          alertType: 'price_drop',
          message: `Price dropped: ${prop.address.full} from $${existing.price.toLocaleString()} to $${prop.price.toLocaleString()}`,
          propertyData: prop,
          oldPrice: existing.price,
          newPrice: prop.price,
          isRead: false,
          createdAt: new Date().toISOString()
        });
      } else if (existing.price < prop.price) {
        // Price increase
        alerts.push({
          searchId,
          propertyId: prop.id,
          alertType: 'price_increase',
          message: `Price increased: ${prop.address.full} from $${existing.price.toLocaleString()} to $${prop.price.toLocaleString()}`,
          propertyData: prop,
          oldPrice: existing.price,
          newPrice: prop.price,
          isRead: false,
          createdAt: new Date().toISOString()
        });
      } else if (existing.status === 'off_market' && prop.listing.status === 'active') {
        // Back on market
        alerts.push({
          searchId,
          propertyId: prop.id,
          alertType: 'back_on_market',
          message: `Back on market: ${prop.address.full} - $${prop.price.toLocaleString()}`,
          propertyData: prop,
          newPrice: prop.price,
          isRead: false,
          createdAt: new Date().toISOString()
        });
      }
    }

    // Check for status changes (sold, off market)
    const propertyIds = currentProperties.map(p => p.id);
    const previouslyActive = await this.getPreviouslyActiveProperties(searchId, propertyIds);
    
    for (const prev of previouslyActive) {
      const stillActive = currentProperties.find(p => p.id === prev.property_id);
      if (!stillActive) {
        // Property no longer active - likely sold or off market
        const prop: Property = {
          id: prev.property_id,
          source: prev.source,
          address: {
            street: prev.street,
            city: prev.city,
            state: prev.state,
            zipCode: prev.zip_code,
            full: prev.address_full
          },
          price: prev.price,
          details: {
            bedrooms: prev.bedrooms,
            bathrooms: prev.bathrooms,
            sqft: prev.sqft,
            lotSize: prev.lot_size,
            yearBuilt: prev.year_built,
            propertyType: prev.property_type as any
          },
          listing: {
            status: 'sold',
            listedDate: prev.listed_date,
            daysOnMarket: prev.days_on_market
          }
        };

        alerts.push({
          searchId,
          propertyId: prev.property_id,
          alertType: 'status_change',
          message: `No longer active: ${prev.address_full} (was $${prev.price.toLocaleString()})`,
          propertyData: prop,
          newPrice: prev.price,
          isRead: false,
          createdAt: new Date().toISOString()
        });
      }
    }

    return alerts;
  }

  private async getPreviouslyActiveProperties(searchId: number, excludeIds: string[]): Promise<PropertyRecord[]> {
    if (!this.db) return [];

    const placeholders = excludeIds.length > 0 ? excludeIds.map(() => '?').join(',') : 'NULL';
    
    return new Promise((resolve, reject) => {
      this.db!.all(
        `SELECT DISTINCT p.* FROM properties p
         INNER JOIN alerts a ON p.property_id = a.property_id
         WHERE a.search_id = ? AND p.status = 'active'
         ${excludeIds.length > 0 ? `AND p.property_id NOT IN (${placeholders})` : ''}`,
        [searchId, ...excludeIds],
        (err, rows: PropertyRecord[]) => {
          if (err) {
            reject(err);
            return;
          }
          resolve(rows);
        }
      );
    });
  }

  private async saveAlert(alert: PropertyAlert): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        `INSERT INTO alerts 
         (search_id, property_id, alert_type, message, property_data, old_price, new_price)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          alert.searchId, alert.propertyId, alert.alertType, alert.message,
          JSON.stringify(alert.propertyData), alert.oldPrice || null, alert.newPrice || null
        ],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  private async updateLastChecked(searchId: number): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'UPDATE saved_searches SET last_checked_at = CURRENT_TIMESTAMP WHERE id = ?',
        [searchId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  // Alert management
  async getAlerts(options?: { searchId?: number; unreadOnly?: boolean; limit?: number }): Promise<PropertyAlert[]> {
    await this.waitForInit();
    if (!this.db) return [];

    let sql = 'SELECT * FROM alerts WHERE 1=1';
    const params: any[] = [];

    if (options?.searchId) {
      sql += ' AND search_id = ?';
      params.push(options.searchId);
    }

    if (options?.unreadOnly) {
      sql += ' AND is_read = 0';
    }

    sql += ' ORDER BY created_at DESC';

    if (options?.limit) {
      sql += ' LIMIT ?';
      params.push(options.limit);
    }

    return new Promise((resolve, reject) => {
      this.db!.all(sql, params, (err, rows: AlertRecord[]) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(rows.map(row => this.mapAlertRecord(row)));
      });
    });
  }

  async markAlertRead(id: number): Promise<boolean> {
    await this.waitForInit();
    if (!this.db) return false;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'UPDATE alerts SET is_read = 1 WHERE id = ?',
        [id],
        function(this: sqlite3.RunResult, err: Error | null) {
          if (err) {
            reject(err);
            return;
          }
          resolve(this.changes > 0);
        }
      );
    });
  }

  async markAllAlertsRead(searchId?: number): Promise<number> {
    await this.waitForInit();
    if (!this.db) return 0;

    let sql = 'UPDATE alerts SET is_read = 1 WHERE is_read = 0';
    const params: any[] = [];

    if (searchId) {
      sql += ' AND search_id = ?';
      params.push(searchId);
    }

    return new Promise((resolve, reject) => {
      this.db!.run(sql, params, function(this: sqlite3.RunResult, err: Error | null) {
        if (err) {
          reject(err);
          return;
        }
        resolve(this.changes);
      });
    });
  }

  async deleteAlert(id: number): Promise<boolean> {
    await this.waitForInit();
    if (!this.db) return false;

    return new Promise((resolve, reject) => {
      this.db!.run(
        'DELETE FROM alerts WHERE id = ?',
        [id],
        function(this: sqlite3.RunResult, err: Error | null) {
          if (err) {
            reject(err);
            return;
          }
          resolve(this.changes > 0);
        }
      );
    });
  }

  private mapAlertRecord(row: AlertRecord): PropertyAlert {
    return {
      id: row.id,
      searchId: row.search_id,
      propertyId: row.property_id,
      alertType: row.alert_type as any,
      message: row.message,
      propertyData: JSON.parse(row.property_data),
      oldPrice: row.old_price || undefined,
      newPrice: row.new_price || undefined,
      isRead: row.is_read === 1,
      createdAt: row.created_at
    };
  }

  // Price history
  async getPriceHistory(propertyId: string): Promise<Array<{ date: string; price: number; event: string }>> {
    await this.waitForInit();
    if (!this.db) return [];

    return new Promise((resolve, reject) => {
      this.db!.all(
        'SELECT * FROM price_history WHERE property_id = ? ORDER BY recorded_at ASC',
        [propertyId],
        (err, rows: PriceHistoryRecord[]) => {
          if (err) {
            reject(err);
            return;
          }
          resolve(rows.map(row => ({
            date: row.recorded_at,
            price: row.price,
            event: row.event
          })));
        }
      );
    });
  }

  // Stats
  async getStats(): Promise<{
    totalSavedSearches: number;
    totalTrackedProperties: number;
    totalAlerts: number;
    unreadAlerts: number;
  }> {
    await this.waitForInit();
    if (!this.db) {
      return { totalSavedSearches: 0, totalTrackedProperties: 0, totalAlerts: 0, unreadAlerts: 0 };
    }

    return new Promise((resolve, reject) => {
      this.db!.get(
        `SELECT 
          (SELECT COUNT(*) FROM saved_searches) as total_searches,
          (SELECT COUNT(*) FROM properties) as total_properties,
          (SELECT COUNT(*) FROM alerts) as total_alerts,
          (SELECT COUNT(*) FROM alerts WHERE is_read = 0) as unread_alerts`,
        (err, row: any) => {
          if (err) {
            reject(err);
            return;
          }
          resolve({
            totalSavedSearches: row.total_searches,
            totalTrackedProperties: row.total_properties,
            totalAlerts: row.total_alerts,
            unreadAlerts: row.unread_alerts
          });
        }
      );
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; message: string; apiAvailable: boolean }> {
    try {
      await this.waitForInit();
      
      const apiAvailable = !!this.zillowApiKey;
      
      return {
        status: 'healthy',
        message: apiAvailable 
          ? 'Property alerts skill is operational with Zillow API'
          : 'Property alerts skill is operational (simulated mode - set ZILLOW_API_KEY for real data)',
        apiAvailable
      };
    } catch (err) {
      return {
        status: 'unhealthy',
        message: `Health check failed: ${err}`,
        apiAvailable: false
      };
    }
  }

  async close(): Promise<void> {
    if (this.db) {
      await this.waitForInit();
      return new Promise((resolve, reject) => {
        this.db!.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
  }
}

export default PropertyAlertsSkill;
