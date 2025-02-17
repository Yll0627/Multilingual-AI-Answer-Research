'use client'
import { useState } from 'react'

const LANGUAGES = [
  { code: "EN", name: "English" },
  { code: "DE", name: "German" },
  { code: "FR", name: "French" },
  { code: "JA", name: "Japanese" }
]

export default function Home() {
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [selectedLanguage, setSelectedLanguage] = useState(null)
  const [isMultiLingual, setIsMultiLingual] = useState(true)

  const handleTranslate = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/translate/auto', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          target_langs: ["EN", "DE", "FR", "JA"],
          single_language: isMultiLingual ? null : selectedLanguage,
          analyze: isMultiLingual,
          question_response: true
        }),
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Translation error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Multilingual AI System</h1>
        
        <div className="mb-6">
          <textarea
            className="w-full p-4 border rounded-lg mb-4"
            rows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text to translate..."
          />
          
          <div className="flex items-center gap-4 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isMultiLingual}
                onChange={(e) => setIsMultiLingual(e.target.checked)}
                className="mr-2"
              />
              Multi-language Mode
            </label>
            
            {!isMultiLingual && (
              <select
                value={selectedLanguage || ''}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="p-2 border rounded"
                disabled={isMultiLingual}
              >
                <option value="">Select Language</option>
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          <button
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
            onClick={handleTranslate}
            disabled={loading || (!isMultiLingual && !selectedLanguage)}
          >
            {loading ? 'Processing...' : 'Translate & Analyze'}
          </button>
        </div>

        {result && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Translations</h2>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(result.translations).map(([lang, text]) => (
                  <div key={lang} className="border p-4 rounded">
                    <div className="font-medium">{lang}</div>
                    <div>{text}</div>
                  </div>
                ))}
              </div>
            </div>

            {result.analysis && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4">Translation Analysis</h2>
                <p className="whitespace-pre-line">{result.analysis}</p>
              </div>
            )}

            {result.question_responses && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4">AI Responses</h2>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.question_responses).map(([lang, response]) => (
                    <div key={lang} className="border p-4 rounded">
                      <div className="font-medium">{lang}</div>
                      <div className="mt-2">{response}</div>
                      {result.english_responses && lang !== 'EN' && (
                        <div className="mt-2 text-gray-600 text-sm">
                          English: {result.english_responses[lang]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
