'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

export default function TermsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const tier = searchParams.get('tier') || 'free'
  const redirect = searchParams.get('redirect') || 'dashboard'
  const email = searchParams.get('email') || ''
  const name = searchParams.get('name') || ''

  const [accepted, setAccepted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleAccept = async () => {
    if (!accepted) return

    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    router.push(`/auth/user-data?tier=${tier}&redirect=${redirect}&email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`)
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900 via-black to-black" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-full max-w-3xl"
      >
        <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-2xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-4">
              <FileText className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Kebijakan dan Ketentuan</h1>
            <p className="text-gray-400">
              Mohon baca dan setujui kebijakan kami untuk melanjutkan
            </p>
          </div>

          <div className="mb-8 max-h-96 overflow-y-auto bg-white/5 border border-white/10 rounded-xl p-6 space-y-4 text-sm">
            <section>
              <h2 className="text-xl font-bold mb-3">1. Ketentuan Umum</h2>
              <p className="text-gray-300 leading-relaxed">
                Dengan menggunakan layanan IKODIO BugBounty, Anda menyetujui untuk terikat dengan syarat dan ketentuan berikut. Jika Anda tidak setuju dengan bagian mana pun dari ketentuan ini, Anda tidak boleh menggunakan layanan kami.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">2. Penggunaan Layanan</h2>
              <ul className="list-disc list-inside text-gray-300 space-y-2">
                <li>Layanan scanning hanya boleh digunakan pada domain/aplikasi yang Anda miliki atau memiliki izin eksplisit</li>
                <li>Dilarang menggunakan layanan untuk aktivitas ilegal atau yang melanggar hukum</li>
                <li>Anda bertanggung jawab atas keamanan akun dan password Anda</li>
                <li>Anda tidak boleh membagikan akses akun kepada pihak ketiga tanpa izin</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">3. Pembayaran dan Langganan</h2>
              <ul className="list-disc list-inside text-gray-300 space-y-2">
                <li>Pembayaran dilakukan di muka untuk periode langganan yang dipilih</li>
                <li>Langganan akan diperpanjang otomatis kecuali dibatalkan sebelum tanggal perpanjangan</li>
                <li>Refund hanya tersedia dalam 7 hari pertama jika layanan tidak dapat digunakan karena kesalahan sistem kami</li>
                <li>Perubahan paket dapat dilakukan kapan saja dengan penyesuaian biaya prorata</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">4. Privasi dan Data</h2>
              <ul className="list-disc list-inside text-gray-300 space-y-2">
                <li>Kami akan melindungi data pribadi Anda sesuai dengan kebijakan privasi kami</li>
                <li>Data hasil scanning disimpan dengan enkripsi dan hanya dapat diakses oleh Anda</li>
                <li>Kami tidak akan membagikan informasi Anda kepada pihak ketiga tanpa persetujuan</li>
                <li>Anda memiliki hak untuk menghapus data Anda kapan saja</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">5. Batasan Tanggung Jawab</h2>
              <p className="text-gray-300 leading-relaxed">
                IKODIO BugBounty menyediakan layanan scanning keamanan sebagaimana adanya. Kami tidak bertanggung jawab atas kerusakan atau kerugian yang timbul dari penggunaan layanan ini. Anda bertanggung jawab penuh atas tindakan yang diambil berdasarkan hasil scanning.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">6. Perubahan Ketentuan</h2>
              <p className="text-gray-300 leading-relaxed">
                Kami berhak mengubah ketentuan ini kapan saja. Perubahan akan diberitahukan melalui email dan akan berlaku setelah 30 hari pemberitahuan. Penggunaan layanan setelah perubahan berarti Anda menyetujui ketentuan yang baru.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-bold mb-3">7. Kontak</h2>
              <p className="text-gray-300 leading-relaxed">
                Jika Anda memiliki pertanyaan tentang ketentuan ini, silakan hubungi kami melalui email di support@ikodio.com atau WhatsApp di 08111285232.
              </p>
            </section>
          </div>

          <div className="mb-6">
            <label className="flex items-start gap-3 cursor-pointer group">
              <div className="relative flex items-center justify-center mt-1">
                <input
                  type="checkbox"
                  checked={accepted}
                  onChange={(e) => setAccepted(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-6 h-6 bg-white/5 border-2 border-white/20 rounded-md peer-checked:bg-white peer-checked:border-white transition-all" />
                {accepted && (
                  <CheckCircle className="absolute w-6 h-6 text-black pointer-events-none" />
                )}
              </div>
              <span className="text-gray-300 group-hover:text-white transition-colors select-none">
                Saya telah membaca dan menyetujui <span className="text-white font-semibold">Kebijakan dan Ketentuan</span> yang berlaku
              </span>
            </label>
          </div>

          {!accepted && (
            <div className="mb-6 p-4 bg-gray-800 border border-gray-600 rounded-xl">
              <p className="text-sm text-gray-300 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                Anda harus menyetujui kebijakan dan ketentuan untuk melanjutkan
              </p>
            </div>
          )}

          <div className="flex gap-4">
            <Link
              href="/"
              className="flex-1 py-4 px-6 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-colors text-center"
            >
              Batal
            </Link>
            <motion.button
              onClick={handleAccept}
              disabled={!accepted || isLoading}
              whileHover={{ scale: accepted ? 1.02 : 1 }}
              whileTap={{ scale: accepted ? 0.98 : 1 }}
              className="flex-1 py-4 px-6 bg-white text-black font-semibold rounded-xl hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  <span>Memproses...</span>
                </>
              ) : (
                <>
                  <span>Setuju dan Lanjutkan</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
