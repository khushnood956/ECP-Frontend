/**
 * Formatting utilities for unified UI presentation of real backend data.
 */

/**
 * Formats an ISO date string to a human-readable format.
 * Example: '2026-08-16T16:42:13.123456' -> 'Aug 16, 2026'
 */
export const formatDate = (dateString, fallback = '—') => {
  if (!dateString) return fallback;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return fallback;
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch (e) {
    return fallback;
  }
};

/**
 * Formats an ISO date string to a date and time string.
 * Example: '2026-08-16T16:42:13' -> 'Aug 16, 2026 · 4:42 PM'
 */
export const formatDateTime = (dateString, fallback = '—') => {
  if (!dateString) return fallback;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return fallback;
    const formattedDate = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
    const formattedTime = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    return `${formattedDate} · ${formattedTime}`;
  } catch (e) {
    return fallback;
  }
};

/**
 * Maps database enum values/API status keys to readable UI labels.
 */
export const getStatusLabel = (status) => {
  if (!status) return '—';
  const clean = status.toLowerCase().trim();
  switch (clean) {
    case 'submitted':
      return 'Submitted';
    case 'under_review':
      return 'Under Review';
    case 'accepted':
      return 'Accepted';
    case 'rejected':
      return 'Rejected';
    case 'pending':
      return 'Pending';
    case 'verified':
      return 'Verified';
    case 'suspended':
      return 'Suspended';
    default:
      return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ');
  }
};

/**
 * Returns consistent Tailwind/CSS classes for status badges based on status enums.
 */
export const getStatusBadgeClass = (status) => {
  if (!status) return 'bg-gray-100 text-gray-800 border-gray-200';
  const clean = status.toLowerCase().trim();
  switch (clean) {
    case 'submitted':
    case 'pending':
      return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800';
    case 'under_review':
      return 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800';
    case 'accepted':
    case 'verified':
      return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800';
    case 'rejected':
    case 'suspended':
      return 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/30 dark:text-gray-400 dark:border-gray-800';
  }
};

/**
 * Formats currency values cleanly.
 */
export const formatCurrency = (amount, currency = 'USD', fallback = '—') => {
  if (amount === null || amount === undefined) return fallback;
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch (e) {
    return `${amount} ${currency}`;
  }
};

/**
 * Formats null/undefined fields to standard placeholders.
 */
export const formatNullable = (value, fallback = '—') => {
  if (value === null || value === undefined || String(value).trim() === '') return fallback;
  return value;
};

/**
 * Safely formats first name and last name.
 */
export const formatName = (firstName, lastName, fallback = 'Anonymous Student') => {
  const first = (firstName || '').trim();
  const last = (lastName || '').trim();
  if (!first && !last) return fallback;
  return `${first} ${last}`.trim();
};

/**
 * Returns a shortened string of UUIDs/IDs for scanner-friendly interfaces.
 */
export const truncateId = (id, length = 8) => {
  if (!id) return '';
  if (id.length <= length) return id;
  return `${id.slice(0, length)}...`;
};
