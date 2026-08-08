/**
 * chapa.js
 * --------
 * Thin wrapper around the Chapa payment API (https://api.chapa.co/v1).
 * Currency is Ethiopian Birr (ETB).
 *
 * SECURITY NOTE:
 *   The Chapa *secret* key should never ship in client-side code in production.
 *   For this mini app we read VITE_CHAPA_SECRET_KEY from env, which is fine for
 *   development / demo. In production, route these calls through a small
 *   serverless endpoint that holds the real secret server-side.
 */

const CHAPA_BASE = 'https://api.chapa.co/v1'
const CURRENCY = 'ETB'

function getApiKey() {
  const key = import.meta.env.VITE_CHAPA_SECRET_KEY
  if (!key) {
    // eslint-disable-next-line no-console
    console.warn(
      '[chapa] VITE_CHAPA_SECRET_KEY is not set. Payment calls will fail in production. ' +
      'For local UI testing, see mockMode below.'
    )
  }
  return key
}

/**
 * Generate a unique transaction reference.
 * Format: cafe-<timestamp>-<random>
 */
export function generateTxRef() {
  const ts = Date.now().toString(36)
  const rand = Math.random().toString(36).slice(2, 8)
  return `cafe-${ts}-${rand}`
}

/**
 * Initialize a Chapa payment session.
 *
 * @param {Object} params
 * @param {number} params.amount      Amount in ETB
 * @param {string} params.email       Customer email
 * @param {string} params.firstName   Customer first name
 * @param {string} [params.lastName]  Customer last name
 * @param {string} [params.txRef]     Transaction reference (auto-generated if omitted)
 * @param {string} [params.callbackUrl]
 * @param {string} [params.returnUrl]
 * @param {string} [params.description]
 * @returns {Promise<{ status: 'success'|'failed', txRef: string, checkoutUrl: string|null, raw: any }>}
 */
export async function initializePayment({
  amount,
  email,
  firstName,
  lastName = '',
  txRef,
  callbackUrl,
  returnUrl,
  description = 'Cafe order',
}) {
  const key = getApiKey()
  const ref = txRef || generateTxRef()

  // ---------- Mock mode (for local UI testing without a real key) ----------
  if (!key || key.startsWith('CHASECK_TESTXXXX')) {
    // eslint-disable-next-line no-console
    console.info('[chapa] mock initializePayment -> ', { amount, email, firstName, ref })
    await new Promise((r) => setTimeout(r, 1200)) // simulate network
    return {
      status: 'success',
      txRef: ref,
      checkoutUrl: null,
      raw: { mocked: true },
    }
  }

  // ---------- Real call ----------
  try {
    const res = await fetch(`${CHAPA_BASE}/transaction/initialize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${key}`,
      },
      body: JSON.stringify({
        amount: String(amount),
        currency: CURRENCY,
        email,
        first_name: firstName,
        last_name: lastName,
        tx_ref: ref,
        callback_url: callbackUrl || window.location.href,
        return_url: returnUrl || window.location.href,
        customization: {
          title: 'Cafe Mini App',
          description,
        },
      }),
    })
    const data = await res.json()
    if (data?.status === 'success' || data?.data?.checkout_url) {
      return {
        status: 'success',
        txRef: ref,
        checkoutUrl: data.data?.checkout_url || null,
        raw: data,
      }
    }
    return { status: 'failed', txRef: ref, checkoutUrl: null, raw: data }
  } catch (err) {
    return {
      status: 'failed',
      txRef: ref,
      checkoutUrl: null,
      raw: { error: String(err) },
    }
  }
}

/**
 * Verify a Chapa payment by transaction reference.
 *
 * @param {string} txRef
 * @returns {Promise<{ status: 'success'|'failed'|'pending', paid: boolean, raw: any }>}
 */
export async function verifyPayment(txRef) {
  const key = getApiKey()

  // ---------- Mock mode ----------
  if (!key || key.startsWith('CHASECK_TESTXXXX')) {
    // eslint-disable-next-line no-console
    console.info('[chapa] mock verifyPayment -> ', txRef)
    await new Promise((r) => setTimeout(r, 900))
    return { status: 'success', paid: true, raw: { mocked: true } }
  }

  try {
    const res = await fetch(`${CHAPA_BASE}/transaction/verify/${txRef}`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${key}` },
    })
    const data = await res.json()
    const paid =
      data?.status === 'success' &&
      (data?.data?.status === 'success' || data?.data?.status === 'paid')
    return {
      status: paid ? 'success' : 'failed',
      paid,
      raw: data,
    }
  } catch (err) {
    return { status: 'failed', paid: false, raw: { error: String(err) } }
  }
}

/**
 * Open the Chapa checkout page (or simulate success in mock mode).
 * Returns true if the user completed payment, false otherwise.
 */
export async function openCheckout(checkoutUrl) {
  if (!checkoutUrl) {
    // Mock mode — just simulate a successful return.
    await new Promise((r) => setTimeout(r, 600))
    return true
  }
  // In Telegram Mini App, opening an external URL requires tg.openLink.
  // In a browser, fall back to opening in a new tab.
  try {
    const tg = window?.Telegram?.WebApp
    if (tg?.openLink) {
      tg.openLink(checkoutUrl)
    } else {
      window.open(checkoutUrl, '_blank', 'noopener,noreferrer')
    }
    return true
  } catch (_) {
    return false
  }
}
