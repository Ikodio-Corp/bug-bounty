'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Building, Mail, Phone, MapPin, Briefcase, Users, FileText, MessageSquare, DollarSign, Send, AlertCircle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function EnterpriseInquiryPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    companyName: '',
    companyEmail: '',
    companyPhone: '',
    industry: '',
    companySize: '',
    currentTools: '',
    requirements: '',
    budgetRange: '',
    contactMethod: 'whatsapp'
  })

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.companyName) newErrors.companyName = 'Nama perusahaan wajib diisi'
    if (!formData.companyEmail) newErrors.companyEmail = 'Email wajib diisi'
    else if (!/\S+@\S+\.\S+/.test(formData.companyEmail)) 
      newErrors.companyEmail = 'Format email tidak valid'
    if (!formData.companyPhone) newErrors.companyPhone = 'Nomor telepon wajib diisi'
    else if (!/^[0-9]{10,13}$/.test(formData.companyPhone.replace(/[-\s]/g, ''))) 
      newErrors.companyPhone = 'Format nomor telepon tidak valid'
    if (!formData.industry) newErrors.industry = 'Sektor bisnis wajib diisi'
    if (!formData.companySize) newErrors.companySize = 'Ukuran perusahaan wajib dipilih'
    if (!formData.requirements) newErrors.requirements = 'Kebutuhan spesifik wajib diisi'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))

      const message = `*IKODIO BugBounty - Enterprise Inquiry*

*Informasi Perusahaan:*
Nama Perusahaan: ${formData.companyName}
Email: ${formData.companyEmail}
Telepon: ${formData.companyPhone}
Sektor Bisnis: ${formData.industry}
Ukuran: ${formData.companySize}

*Security Tools Saat Ini:*
${formData.currentTools || 'Tidak disebutkan'}

*Kebutuhan Spesifik:*
${formData.requirements}

*Budget Range:*
${formData.budgetRange || 'Akan didiskusikan'}

*Metode Kontak Preferensi:*
${formData.contactMethod === 'whatsapp' ? 'WhatsApp' : formData.contactMethod === 'email' ? 'Email' : 'Phone Call'}

---
Dikirim dari: ikodio.com/enterprise-inquiry`

      const encodedMessage = encodeURIComponent(message)
      const whatsappUrl = `https://wa.me/628111285232?text=${encodedMessage}`
      
      window.open(whatsappUrl, '_blank')
      
      setTimeout(() => {
        router.push('/')
      }, 2000)
      
    } catch (error) {
      setErrors({ submit: 'Terjadi kesalahan. Silakan coba lagi.' })
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-gray-900" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-3xl my-8"
      >
        <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-2xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-4">
              <Building className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Enterprise Inquiry</h1>
            <p className="text-gray-400">
              Lengkapi form ini dan tim kami akan menghubungi Anda melalui WhatsApp
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Nama Perusahaan *</label>
                <div className="relative">
                  <Building className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleChange}
                    className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyName ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                    placeholder="PT. Nama Perusahaan"
                  />
                </div>
                {errors.companyName && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyName}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Email Perusahaan *</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="email"
                    name="companyEmail"
                    value={formData.companyEmail}
                    onChange={handleChange}
                    className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyEmail ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                    placeholder="contact@company.com"
                  />
                </div>
                {errors.companyEmail && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyEmail}</p>}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Nomor Telepon *</label>
                <div className="relative">
                  <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="tel"
                    name="companyPhone"
                    value={formData.companyPhone}
                    onChange={handleChange}
                    className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyPhone ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                    placeholder="021-12345678"
                  />
                </div>
                {errors.companyPhone && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyPhone}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Sektor Bisnis *</label>
                <div className="relative">
                  <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    name="industry"
                    value={formData.industry}
                    onChange={handleChange}
                    className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.industry ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                    placeholder="Teknologi, Finance, Retail, dll"
                  />
                </div>
                {errors.industry && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.industry}</p>}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Ukuran Perusahaan *</label>
              <div className="relative">
                <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 pointer-events-none" />
                <select
                  name="companySize"
                  value={formData.companySize}
                  onChange={handleChange}
                  className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companySize ? 'border-white' : 'border-white/10'} rounded-xl text-white focus:outline-none focus:border-white/30 appearance-none cursor-pointer`}
                >
                  <option value="" className="bg-black">Pilih ukuran perusahaan</option>
                  <option value="<10" className="bg-black">Kurang dari 10 karyawan</option>
                  <option value="10-50" className="bg-black">10-50 karyawan</option>
                  <option value="50-200" className="bg-black">50-200 karyawan</option>
                  <option value="200-1000" className="bg-black">200-1000 karyawan</option>
                  <option value="1000+" className="bg-black">Lebih dari 1000 karyawan</option>
                </select>
              </div>
              {errors.companySize && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companySize}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Security Tools yang Digunakan Saat Ini</label>
              <div className="relative">
                <FileText className="absolute left-4 top-4 w-5 h-5 text-gray-500" />
                <textarea
                  name="currentTools"
                  value={formData.currentTools}
                  onChange={handleChange}
                  rows={3}
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 resize-none"
                  placeholder="Contoh: Burp Suite, OWASP ZAP, Nessus, dll (opsional)"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Kebutuhan Spesifik *</label>
              <div className="relative">
                <MessageSquare className="absolute left-4 top-4 w-5 h-5 text-gray-500" />
                <textarea
                  name="requirements"
                  value={formData.requirements}
                  onChange={handleChange}
                  rows={5}
                  className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.requirements ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30 resize-none`}
                  placeholder="Jelaskan kebutuhan security assessment Anda, target aplikasi/sistem, timeline, dll"
                />
              </div>
              {errors.requirements && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.requirements}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Budget Range (Opsional)</label>
              <div className="relative">
                <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  name="budgetRange"
                  value={formData.budgetRange}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30"
                  placeholder="Rp 10.000.000 - Rp 50.000.000 (opsional)"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Metode Kontak Preferensi</label>
              <div className="grid grid-cols-3 gap-4">
                <label className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                  formData.contactMethod === 'whatsapp' 
                    ? 'bg-white text-black border-white' 
                    : 'bg-white/5 text-white border-white/10 hover:border-white/30'
                }`}>
                  <input
                    type="radio"
                    name="contactMethod"
                    value="whatsapp"
                    checked={formData.contactMethod === 'whatsapp'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <Send className="w-6 h-6 mb-2" />
                  <span className="text-sm font-semibold">WhatsApp</span>
                </label>
                <label className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                  formData.contactMethod === 'email' 
                    ? 'bg-white text-black border-white' 
                    : 'bg-white/5 text-white border-white/10 hover:border-white/30'
                }`}>
                  <input
                    type="radio"
                    name="contactMethod"
                    value="email"
                    checked={formData.contactMethod === 'email'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <Mail className="w-6 h-6 mb-2" />
                  <span className="text-sm font-semibold">Email</span>
                </label>
                <label className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                  formData.contactMethod === 'phone' 
                    ? 'bg-white text-black border-white' 
                    : 'bg-white/5 text-white border-white/10 hover:border-white/30'
                }`}>
                  <input
                    type="radio"
                    name="contactMethod"
                    value="phone"
                    checked={formData.contactMethod === 'phone'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <Phone className="w-6 h-6 mb-2" />
                  <span className="text-sm font-semibold">Phone Call</span>
                </label>
              </div>
            </div>

            {errors.submit && (
              <div className="p-4 bg-white/5 border border-white/20 rounded-xl">
                <p className="text-sm text-gray-300 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {errors.submit}
                </p>
              </div>
            )}

            <div className="flex gap-4 pt-4">
              <Link
                href="/"
                className="flex-1 py-4 px-6 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-colors text-center"
              >
                Batal
              </Link>
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex-1 py-4 px-6 bg-white text-black font-semibold rounded-xl hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                    <span>Mengarahkan ke WhatsApp...</span>
                  </>
                ) : (
                  <>
                    <span>Hubungi Sales</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </motion.button>
            </div>
          </form>

          <div className="mt-6 p-4 bg-white/5 border border-white/10 rounded-xl">
            <p className="text-sm text-gray-400 text-center">
              Setelah submit, Anda akan diarahkan ke WhatsApp Business kami di <span className="text-white font-semibold">08111285232</span>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
