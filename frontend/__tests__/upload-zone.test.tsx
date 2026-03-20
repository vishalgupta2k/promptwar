import { render, screen } from '@testing-library/react'
import { UploadZone } from '../components/lexsimple/upload-zone'
import { describe, it, expect, vi } from 'vitest'

describe('UploadZone', () => {
  it('renders the upload title correctly', () => {
    const mockUpload = vi.fn()
    const mockPaste = vi.fn()
    
    render(<UploadZone onFileUpload={mockUpload} onTextPaste={mockPaste} />)
    
    // Check if main UI elements exist
    expect(screen.getByText(/Drop your contract here/i)).toBeInTheDocument()
    expect(screen.getByText(/PDF, DOCX, TXT — up to 50 pages/i)).toBeInTheDocument()
    expect(screen.getByText(/Paste contract text/i)).toBeInTheDocument()
  })
})
