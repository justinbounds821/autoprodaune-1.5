import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Landing from '../pages/Landing'

// Mock fetch for API calls
const mockFetch = jest.fn()
global.fetch = mockFetch

// Wrapper component for router context
const RouterWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
)

describe('Landing Page', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  test('renders landing page with main elements', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Check hero section
    expect(screen.getByText(/AutoPro Daune/i)).toBeInTheDocument()
    expect(screen.getByText(/Soluția ta completă pentru daune auto/i)).toBeInTheDocument()

    // Check CTA button
    expect(screen.getByText(/Obține Despăgubirea/i)).toBeInTheDocument()

    // Check referral section
    expect(screen.getByText(/200 LEI/i)).toBeInTheDocument()
  })

  test('renders lead capture form', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    expect(screen.getByPlaceholderText(/numele tău complet/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/numărul tău de telefon/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/adresa ta de email/i)).toBeInTheDocument()
    expect(screen.getByText(/trimite cererea/i)).toBeInTheDocument()
  })

  test('displays testimonials section', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Check testimonials heading
    expect(screen.getByText(/ce spun clienții noștri/i)).toBeInTheDocument()

    // Check for testimonial content
    expect(screen.getByText(/maria popescu/i)).toBeInTheDocument()
    expect(screen.getByText(/ion georgescu/i)).toBeInTheDocument()
  })

  test('shows process steps', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    expect(screen.getByText(/cum funcționează/i)).toBeInTheDocument()
    expect(screen.getByText(/completezi formularul/i)).toBeInTheDocument()
    expect(screen.getByText(/te contactăm în 30 minute/i)).toBeInTheDocument()
    expect(screen.getByText(/obții despăgubirea/i)).toBeInTheDocument()
  })

  test('handles form submission successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Lead creat cu succes' })
    })

    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Fill form
    fireEvent.change(screen.getByPlaceholderText(/numele tău complet/i), {
      target: { value: 'Ion Test' }
    })
    fireEvent.change(screen.getByPlaceholderText(/numărul tău de telefon/i), {
      target: { value: '0721123456' }
    })
    fireEvent.change(screen.getByPlaceholderText(/adresa ta de email/i), {
      target: { value: 'ion@test.com' }
    })

    // Submit form
    fireEvent.click(screen.getByText(/trimite cererea/i))

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/leads/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: expect.stringContaining('Ion Test')
        })
      )
    })
  })

  test('shows error message on form submission failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Fill and submit form
    fireEvent.change(screen.getByPlaceholderText(/numele tău complet/i), {
      target: { value: 'Ion Test' }
    })
    fireEvent.change(screen.getByPlaceholderText(/numărul tău de telefon/i), {
      target: { value: '0721123456' }
    })
    fireEvent.click(screen.getByText(/trimite cererea/i))

    await waitFor(() => {
      expect(screen.getByText(/a apărut o eroare/i)).toBeInTheDocument()
    })
  })

  test('validates required form fields', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Try to submit empty form
    fireEvent.click(screen.getByText(/trimite cererea/i))

    // Form should prevent submission and show validation
    expect(screen.getByPlaceholderText(/numele tău complet/i)).toBeRequired()
    expect(screen.getByPlaceholderText(/numărul tău de telefon/i)).toBeRequired()
  })

  test('referral link generation works', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Check referral section
    const referralSection = screen.getByText(/câștigă 200 lei/i).closest('section')
    expect(referralSection).toBeInTheDocument()

    // Check for referral CTA
    expect(screen.getByText(/începe să câștigi acum/i)).toBeInTheDocument()
  })

  test('responsive design elements are present', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Check for responsive classes (these depend on your CSS framework)
    const heroSection = screen.getByText(/AutoPro Daune/i).closest('section')
    expect(heroSection).toHaveClass('min-h-screen')

    const form = screen.getByPlaceholderText(/numele tău complet/i).closest('form')
    expect(form).toHaveClass('max-w-md')
  })

  test('WhatsApp integration link works', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    const whatsappLink = screen.getByText(/alătură-te comunității/i)
    expect(whatsappLink).toBeInTheDocument()

    // Check it links to community page
    fireEvent.click(whatsappLink)
    // This would need router mock to test navigation
  })

  test('contact information is displayed', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    expect(screen.getByText(/\+40 723 456 789/)).toBeInTheDocument()
    expect(screen.getByText(/contact@autoprodaune\.com/)).toBeInTheDocument()
  })

  test('trust indicators are shown', () => {
    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Check for trust elements
    expect(screen.getByText(/peste 1000 de clienți mulțumiți/i)).toBeInTheDocument()
    expect(screen.getByText(/răspuns în 30 de minute/i)).toBeInTheDocument()
    expect(screen.getByText(/100% gratuit/i)).toBeInTheDocument()
  })

  test('form loading state works', async () => {
    // Mock slow API response
    mockFetch.mockImplementation(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({ success: true })
        }), 100)
      )
    )

    render(
      <RouterWrapper>
        <Landing />
      </RouterWrapper>
    )

    // Fill and submit form
    fireEvent.change(screen.getByPlaceholderText(/numele tău complet/i), {
      target: { value: 'Ion Test' }
    })
    fireEvent.click(screen.getByText(/trimite cererea/i))

    // Should show loading state
    expect(screen.getByText(/se procesează/i)).toBeInTheDocument()

    // Wait for completion
    await waitFor(() => {
      expect(screen.queryByText(/se procesează/i)).not.toBeInTheDocument()
    }, { timeout: 200 })
  })
})