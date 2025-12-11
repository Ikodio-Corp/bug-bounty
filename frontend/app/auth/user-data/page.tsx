'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, User, Building, Phone, MapPin, CreditCard, Briefcase, Users, FileText, AlertCircle } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

type UserType = 'individual' | 'company'

export default function UserDataPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const tier = searchParams.get('tier') || 'free'
  const redirect = searchParams.get('redirect') || 'dashboard'
  const email = searchParams.get('email') || ''
  const name = searchParams.get('name') || ''

  const [userType, setUserType] = useState<UserType>('individual')
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [individualData, setIndividualData] = useState({
    fullName: name,
    phone: '',
    address: '',
    idCard: ''
  })

  const [companyData, setCompanyData] = useState({
    companyName: '',
    companyEmail: email,
    companyPhone: '',
    companyAddress: '',
    npwp: '',
    businessSector: '',
    companySize: '',
    picName: name,
    picPosition: ''
  })

  const validateIndividualForm = () => {
    const newErrors: Record<string, string> = {}

    if (!individualData.fullName) newErrors.fullName = 'Nama lengkap wajib diisi'
    if (!individualData.phone) newErrors.phone = 'Nomor telepon wajib diisi'
    else if (!/^[0-9]{10,13}$/.test(individualData.phone.replace(/[-\s]/g, ''))) 
      newErrors.phone = 'Format nomor telepon tidak valid'
    if (!individualData.address) newErrors.address = 'Alamat wajib diisi'
    if (!individualData.idCard) newErrors.idCard = 'Nomor KTP wajib diisi'
    else if (!/^[0-9]{16}$/.test(individualData.idCard)) 
      newErrors.idCard = 'Nomor KTP harus 16 digit'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const validateCompanyForm = () => {
    const newErrors: Record<string, string> = {}

    if (!companyData.companyName) newErrors.companyName = 'Nama perusahaan wajib diisi'
    if (!companyData.companyEmail) newErrors.companyEmail = 'Email perusahaan wajib diisi'
    else if (!/\S+@\S+\.\S+/.test(companyData.companyEmail)) 
      newErrors.companyEmail = 'Format email tidak valid'
    if (!companyData.companyPhone) newErrors.companyPhone = 'Nomor telepon wajib diisi'
    else if (!/^[0-9]{10,13}$/.test(companyData.companyPhone.replace(/[-\s]/g, ''))) 
      newErrors.companyPhone = 'Format nomor telepon tidak valid'
    if (!companyData.companyAddress) newErrors.companyAddress = 'Alamat perusahaan wajib diisi'
    if (!companyData.npwp) newErrors.npwp = 'NPWP wajib diisi'
    else if (!/^[0-9]{15}$/.test(companyData.npwp.replace(/[.-]/g, ''))) 
      newErrors.npwp = 'Format NPWP tidak valid'
    if (!companyData.businessSector) newErrors.businessSector = 'Sektor bisnis wajib diisi'
    if (!companyData.companySize) newErrors.companySize = 'Ukuran perusahaan wajib dipilih'
    if (!companyData.picName) newErrors.picName = 'Nama PIC wajib diisi'
    if (!companyData.picPosition) newErrors.picPosition = 'Jabatan PIC wajib diisi'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const isValid = userType === 'individual' ? validateIndividualForm() : validateCompanyForm()
    if (!isValid) return

    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      if (tier === 'free') {
        router.push('/dashboard')
      } else {
        router.push(`/payment?tier=${tier}`)
      }
    } catch (error) {
      setErrors({ submit: 'Terjadi kesalahan. Silakan coba lagi.' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleIndividualChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setIndividualData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setCompanyData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-2xl my-8"
      >
        <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-2xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-2">Lengkapi Data Anda</h1>
            <p className="text-gray-400">
              Pilih jenis akun dan lengkapi informasi yang diperlukan
            </p>
          </div>

          <div className="flex gap-4 mb-8">
            <button
              type="button"
              onClick={() => setUserType('individual')}
              className={`flex-1 py-4 px-6 rounded-xl border-2 transition-all ${
                userType === 'individual'
                  ? 'bg-white text-black border-white'
                  : 'bg-white/5 text-white border-white/10 hover:border-white/30'
              }`}
            >
              <User className="w-6 h-6 mx-auto mb-2" />
              <div className="font-semibold">Individu</div>
              <div className="text-xs opacity-70 mt-1">Untuk penggunaan pribadi</div>
            </button>
            <button
              type="button"
              onClick={() => setUserType('company')}
              className={`flex-1 py-4 px-6 rounded-xl border-2 transition-all ${
                userType === 'company'
                  ? 'bg-white text-black border-white'
                  : 'bg-white/5 text-white border-white/10 hover:border-white/30'
              }`}
            >
              <Building className="w-6 h-6 mx-auto mb-2" />
              <div className="font-semibold">Perusahaan</div>
              <div className="text-xs opacity-70 mt-1">Untuk bisnis/organisasi</div>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {userType === 'individual' ? (
              <>
                <div>
                  <label className="block text-sm font-medium mb-2">Nama Lengkap</label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      name="fullName"
                      value={individualData.fullName}
                      onChange={handleIndividualChange}
                      className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.fullName ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                      placeholder="Nama lengkap sesuai KTP"
                    />
                  </div>
                  {errors.fullName && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.fullName}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Nomor Telepon</label>
                  <div className="relative">
                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="tel"
                      name="phone"
                      value={individualData.phone}
                      onChange={handleIndividualChange}
                      className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.phone ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                      placeholder="08123456789"
                    />
                  </div>
                  {errors.phone && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.phone}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Alamat Lengkap</label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-4 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      name="address"
                      value={individualData.address}
                      onChange={handleIndividualChange}
                      className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.address ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                      placeholder="Jalan, Kelurahan, Kecamatan, Kota, Provinsi"
                    />
                  </div>
                  {errors.address && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.address}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Nomor KTP</label>
                  <div className="relative">
                    <CreditCard className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      name="idCard"
                      value={individualData.idCard}
                      onChange={handleIndividualChange}
                      maxLength={16}
                      className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.idCard ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                      placeholder="16 digit nomor KTP"
                    />
                  </div>
                  {errors.idCard && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.idCard}</p>}
                </div>
              </>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Nama Perusahaan *</label>
                    <div className="relative">
                      <Building className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                      <input
                        type="text"
                        name="companyName"
                        value={companyData.companyName}
                        onChange={handleCompanyChange}
                        className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyName ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                        placeholder="PT. Nama Perusahaan"
                      />
                    </div>
                    {errors.companyName && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyName}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Email Perusahaan *</label>
                      <input
                        type="email"
                        name="companyEmail"
                        value={companyData.companyEmail}
                        onChange={handleCompanyChange}
                        className={`w-full px-4 py-3 bg-white/5 border ${errors.companyEmail ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                        placeholder="email@company.com"
                      />
                    {errors.companyEmail && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyEmail}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Telepon Perusahaan *</label>
                    <div className="relative">
                      <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                        <input
                          type="tel"
                          name="companyPhone"
                          value={companyData.companyPhone}
                          onChange={handleCompanyChange}
                          className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyPhone ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                          placeholder="021-12345678"
                        />
                    </div>
                    {errors.companyPhone && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyPhone}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">NPWP *</label>
                    <div className="relative">
                      <FileText className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                        <input
                          type="text"
                          name="npwp"
                          value={companyData.npwp}
                          onChange={handleCompanyChange}
                          className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.npwp ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                          placeholder="00.000.000.0-000.000"
                        />
                    </div>
                    {errors.npwp && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.npwp}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Alamat Perusahaan *</label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-4 w-5 h-5 text-gray-500" />
                    <input
                      type="text"
                      name="companyAddress"
                      value={companyData.companyAddress}
                      onChange={handleCompanyChange}
                      className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companyAddress ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                      placeholder="Alamat lengkap kantor"
                    />
                  </div>
                  {errors.companyAddress && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companyAddress}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Sektor Bisnis *</label>
                    <div className="relative">
                      <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                        <input
                          type="text"
                          name="businessSector"
                          value={companyData.businessSector}
                          onChange={handleCompanyChange}
                          className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.businessSector ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                          placeholder="Teknologi, Finance, dll"
                        />
                    </div>
                    {errors.businessSector && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.businessSector}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Ukuran Perusahaan *</label>
                    <div className="relative">
                      <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 pointer-events-none" />
                      <select
                        name="companySize"
                        value={companyData.companySize}
                        onChange={handleCompanyChange}
                        className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.companySize ? 'border-white' : 'border-white/10'} rounded-xl text-white focus:outline-none focus:border-white/30 appearance-none cursor-pointer`}
                      >
                        <option value="" className="bg-black">Pilih ukuran</option>
                        <option value="<10" className="bg-black">Kurang dari 10 karyawan</option>
                        <option value="10-50" className="bg-black">10-50 karyawan</option>
                        <option value="50-200" className="bg-black">50-200 karyawan</option>
                        <option value="200-1000" className="bg-black">200-1000 karyawan</option>
                        <option value="1000+" className="bg-black">Lebih dari 1000 karyawan</option>
                      </select>
                    </div>
                    {errors.companySize && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.companySize}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Nama PIC *</label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                        <input
                          type="text"
                          name="picName"
                          value={companyData.picName}
                          onChange={handleCompanyChange}
                          className={`w-full pl-12 pr-4 py-3 bg-white/5 border ${errors.picName ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                          placeholder="Person In Charge"
                        />
                    </div>
                    {errors.picName && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.picName}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Jabatan PIC *</label>
                      <input
                        type="text"
                        name="picPosition"
                        value={companyData.picPosition}
                        onChange={handleCompanyChange}
                        className={`w-full px-4 py-3 bg-white/5 border ${errors.picPosition ? 'border-white' : 'border-white/10'} rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-white/30`}
                        placeholder="CTO, IT Manager, dll"
                      />
                    {errors.picPosition && <p className="mt-2 text-sm text-gray-300 flex items-center gap-1"><AlertCircle className="w-4 h-4" />{errors.picPosition}</p>}
                  </div>
                </div>
              </>
            )}

            {errors.submit && (
              <div className="p-4 bg-white/10 border border-white/20 rounded-xl">
                <p className="text-sm text-gray-300 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {errors.submit}
                </p>
              </div>
            )}

            <div className="flex gap-4 pt-4">
              <Link
                href={`/auth/terms?tier=${tier}&redirect=${redirect}&email=${email}&name=${name}`}
                className="flex-1 py-4 px-6 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-colors text-center"
              >
                Kembali
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
                    <span>Memproses...</span>
                  </>
                ) : (
                  <>
                    <span>{tier === 'free' ? 'Selesai' : 'Lanjut ke Pembayaran'}</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  )
}
