#!/usr/bin/env node

import { PropertyAlertsSkill, PropertySearchCriteria, SavedSearch, Property, PropertyAlert } from './index';

const skill = new PropertyAlertsSkill();

function formatPrice(price: number): string {
  return '$' + price.toLocaleString();
}

function formatProperty(property: Property, compact: boolean = false): string {
  if (compact) {
    return `${property.address.full} - ${formatPrice(property.price)} - ${property.details.bedrooms}bd/${property.details.bathrooms}ba`;
  }
  
  return `
${'─'.repeat(60)}
${property.address.full}
${'─'.repeat(60)}
  Price:        ${formatPrice(property.price)}
  Bedrooms:     ${property.details.bedrooms}
  Bathrooms:    ${property.details.bathrooms}
  Square Feet:  ${property.details.sqft?.toLocaleString() || 'N/A'}
  Property Type: ${property.details.propertyType}
  Status:       ${property.listing.status}
  Days on Market: ${property.listing.daysOnMarket}
  ${property.details.yearBuilt ? `Year Built:   ${property.details.yearBuilt}` : ''}
  ${property.details.lotSize ? `Lot Size:     ${property.details.lotSize.toLocaleString()} sqft` : ''}
  ${property.features ? `Features:     ${property.features.join(', ')}` : ''}
  ${property.description ? `\nDescription:  ${property.description}` : ''}
  ${property.url ? `\nURL:          ${property.url}` : ''}
`;
}

function formatAlert(alert: PropertyAlert, compact: boolean = false): string {
  const typeIcons: Record<string, string> = {
    new_listing: '🏠',
    price_drop: '📉',
    price_increase: '📈',
    status_change: '🔄',
    back_on_market: '🔙'
  };

  if (compact) {
    const icon = typeIcons[alert.alertType] || '🔔';
    return `${icon} ${alert.message}`;
  }

  return `
${'─'.repeat(60)}
${typeIcons[alert.alertType] || '🔔'} ${alert.alertType.replace('_', ' ').toUpperCase()}
${'─'.repeat(60)}
${alert.message}
${alert.oldPrice && alert.newPrice ? `
Price Change: ${formatPrice(alert.oldPrice)} → ${formatPrice(alert.newPrice)} (${((alert.newPrice - alert.oldPrice) / alert.oldPrice * 100).toFixed(1)}%)` : ''}
Received: ${new Date(alert.createdAt).toLocaleString()}
Status: ${alert.isRead ? 'Read' : 'Unread'}
${formatProperty(alert.propertyData, true)}
`;
}

function formatSavedSearch(search: SavedSearch): string {
  const c = search.criteria;
  const filters: string[] = [];
  
  if (c.minPrice || c.maxPrice) {
    filters.push(`Price: ${c.minPrice ? formatPrice(c.minPrice) : 'Any'} - ${c.maxPrice ? formatPrice(c.maxPrice) : 'Any'}`);
  }
  if (c.minBedrooms || c.maxBedrooms) {
    filters.push(`Beds: ${c.minBedrooms || 'Any'} - ${c.maxBedrooms || 'Any'}`);
  }
  if (c.minBathrooms || c.maxBathrooms) {
    filters.push(`Baths: ${c.minBathrooms || 'Any'} - ${c.maxBathrooms || 'Any'}`);
  }
  if (c.propertyTypes) {
    filters.push(`Types: ${c.propertyTypes.join(', ')}`);
  }

  return `
${'─'.repeat(60)}
#${search.id}: ${search.name}
${'─'.repeat(60)}
  Location:     ${c.location}
  ${filters.join('\n  ')}
  Alerts:       ${search.alertEnabled ? 'Enabled' : 'Disabled'}
  Last Checked: ${search.lastCheckedAt ? new Date(search.lastCheckedAt).toLocaleString() : 'Never'}
  Created:      ${new Date(search.createdAt).toLocaleString()}
`;
}

async function searchCommand(args: string[]) {
  const location = args[0];
  if (!location) {
    console.error('Usage: search <location> [--min-price N] [--max-price N] [--beds N] [--baths N]');
    process.exit(1);
  }

  const criteria: PropertySearchCriteria = { location };
  
  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--min-price':
        criteria.minPrice = parseInt(args[++i]);
        break;
      case '--max-price':
        criteria.maxPrice = parseInt(args[++i]);
        break;
      case '--beds':
        criteria.minBedrooms = parseInt(args[++i]);
        break;
      case '--baths':
        criteria.minBathrooms = parseFloat(args[++i]);
        break;
      case '--type':
        criteria.propertyTypes = [args[++i] as any];
        break;
    }
  }

  console.log(`Searching for properties in ${location}...`);
  const results = await skill.searchProperties(criteria);
  
  console.log(`\nFound ${results.totalResults} properties (${results.searchTime}ms)`);
  
  for (const property of results.properties) {
    console.log(formatProperty(property));
  }
}

async function saveSearchCommand(args: string[]) {
  const name = args[0];
  const location = args[1];
  
  if (!name || !location) {
    console.error('Usage: save-search <name> <location> [--min-price N] [--max-price N] [--beds N] [--baths N] [--no-alerts]');
    process.exit(1);
  }

  const criteria: PropertySearchCriteria = { location };
  let alertEnabled = true;
  
  for (let i = 2; i < args.length; i++) {
    switch (args[i]) {
      case '--min-price':
        criteria.minPrice = parseInt(args[++i]);
        break;
      case '--max-price':
        criteria.maxPrice = parseInt(args[++i]);
        break;
      case '--beds':
        criteria.minBedrooms = parseInt(args[++i]);
        break;
      case '--baths':
        criteria.minBathrooms = parseFloat(args[++i]);
        break;
      case '--type':
        criteria.propertyTypes = [args[++i] as any];
        break;
      case '--no-alerts':
        alertEnabled = false;
        break;
    }
  }

  const saved = await skill.saveSearch(name, criteria, alertEnabled);
  console.log(`Saved search "${name}" (ID: ${saved.id})`);
  console.log(`Alerts: ${alertEnabled ? 'Enabled' : 'Disabled'}`);
}

async function listSearchesCommand() {
  const searches = await skill.getSavedSearches();
  
  if (searches.length === 0) {
    console.log('No saved searches found.');
    return;
  }

  console.log(`\n${searches.length} saved search(es):`);
  for (const search of searches) {
    console.log(formatSavedSearch(search));
  }
}

async function deleteSearchCommand(args: string[]) {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: delete-search <id>');
    process.exit(1);
  }

  const success = await skill.deleteSavedSearch(id);
  console.log(success ? `Deleted search #${id}` : `Search #${id} not found`);
}

async function checkCommand(args: string[]) {
  const searchId = args[0] ? parseInt(args[0]) : undefined;
  
  console.log(searchId ? `Checking for alerts on search #${searchId}...` : 'Checking all searches for alerts...');
  
  const alerts = await skill.checkForAlerts(searchId);
  
  if (alerts.length === 0) {
    console.log('No new alerts found.');
    return;
  }

  console.log(`\n${alerts.length} new alert(s) found:`);
  for (const alert of alerts) {
    console.log(formatAlert(alert));
  }
}

async function alertsCommand(args: string[]) {
  const options: { unreadOnly?: boolean; limit?: number } = {};
  
  if (args.includes('--unread')) {
    options.unreadOnly = true;
  }
  
  const limitIndex = args.indexOf('--limit');
  if (limitIndex >= 0 && args[limitIndex + 1]) {
    options.limit = parseInt(args[limitIndex + 1]);
  }

  const alerts = await skill.getAlerts(options);
  
  if (alerts.length === 0) {
    console.log('No alerts found.');
    return;
  }

  console.log(`\n${alerts.length} alert(s):`);
  for (const alert of alerts) {
    console.log(formatAlert(alert));
  }
}

async function readCommand(args: string[]) {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: read <id>');
    process.exit(1);
  }

  const success = await skill.markAlertRead(id);
  console.log(success ? `Marked alert #${id} as read` : `Alert #${id} not found`);
}

async function readAllCommand(args: string[]) {
  const searchId = args[0] ? parseInt(args[0]) : undefined;
  const count = await skill.markAllAlertsRead(searchId);
  console.log(`Marked ${count} alert(s) as read`);
}

async function deleteAlertCommand(args: string[]) {
  const id = parseInt(args[0]);
  if (isNaN(id)) {
    console.error('Usage: delete-alert <id>');
    process.exit(1);
  }

  const success = await skill.deleteAlert(id);
  console.log(success ? `Deleted alert #${id}` : `Alert #${id} not found`);
}

async function historyCommand(args: string[]) {
  const propertyId = args[0];
  if (!propertyId) {
    console.error('Usage: history <property-id>');
    process.exit(1);
  }

  const history = await skill.getPriceHistory(propertyId);
  
  if (history.length === 0) {
    console.log('No price history found for this property.');
    return;
  }

  console.log(`\nPrice History for ${propertyId}:`);
  console.log('─'.repeat(60));
  
  for (const record of history) {
    const date = new Date(record.date).toLocaleDateString();
    console.log(`${date}  ${formatPrice(record.price)}  ${record.event}`);
  }
}

async function statsCommand() {
  const stats = await skill.getStats();
  
  console.log(`
${'─'.repeat(60)}
Property Alerts Statistics
${'─'.repeat(60)}
  Saved Searches:       ${stats.totalSavedSearches}
  Tracked Properties:   ${stats.totalTrackedProperties}
  Total Alerts:         ${stats.totalAlerts}
  Unread Alerts:        ${stats.unreadAlerts}
`);
}

async function healthCommand() {
  const health = await skill.healthCheck();
  
  console.log(`
${'─'.repeat(60)}
Health Check
${'─'.repeat(60)}
  Status:       ${health.status}
  API:          ${health.apiAvailable ? 'Available' : 'Not configured'}
  Message:      ${health.message}
`);
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const commandArgs = args.slice(1);

  try {
    switch (command) {
      case 'search':
        await searchCommand(commandArgs);
        break;
      case 'save-search':
        await saveSearchCommand(commandArgs);
        break;
      case 'list-searches':
      case 'searches':
        await listSearchesCommand();
        break;
      case 'delete-search':
        await deleteSearchCommand(commandArgs);
        break;
      case 'check':
        await checkCommand(commandArgs);
        break;
      case 'alerts':
        await alertsCommand(commandArgs);
        break;
      case 'read':
        await readCommand(commandArgs);
        break;
      case 'read-all':
        await readAllCommand(commandArgs);
        break;
      case 'delete-alert':
        await deleteAlertCommand(commandArgs);
        break;
      case 'history':
        await historyCommand(commandArgs);
        break;
      case 'stats':
        await statsCommand();
        break;
      case 'health':
      case 'status':
        await healthCommand();
        break;
      default:
        console.log(`
Property Alerts - Real Estate Listing Monitor

Usage: property-alerts <command> [options]

Commands:
  search <location>           Search for properties
    --min-price <n>           Minimum price
    --max-price <n>           Maximum price
    --beds <n>                Minimum bedrooms
    --baths <n>               Minimum bathrooms
    --type <type>             Property type (house, condo, townhouse, etc.)

  save-search <name> <loc>    Save a search with alerts
    --no-alerts               Disable alerts for this search

  list-searches               List all saved searches
  delete-search <id>          Delete a saved search

  check [search-id]           Check for new alerts
  alerts                      Show all alerts
    --unread                  Show only unread alerts
    --limit <n>               Limit results

  read <id>                   Mark alert as read
  read-all [search-id]        Mark all alerts as read
  delete-alert <id>           Delete an alert

  history <property-id>       Show price history for a property
  stats                       Show statistics
  health                      Check system health

Examples:
  property-alerts search "Austin, TX" --min-price 300000 --beds 3
  property-alerts save-search "Austin Homes" "Austin, TX" --max-price 500000
  property-alerts check
`);
        process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err);
    process.exit(1);
  } finally {
    await skill.close();
  }
}

main();
