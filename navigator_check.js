(async () => {
  function safeGet(obj, prop) {
    try {
      const val = obj[prop]
      if (typeof val === "function") {
        return {
          type: "function",
          name: val.name,
          length: val.length,
          toString: Function.prototype.toString.call(val)
        }
      }
      return {
        type: typeof val,
        value: val
      }
    } catch (e) {
      return {
        error: e.toString()
      }
    }
  }

  function dumpObject(obj, label) {
    const result = {}
    let current = obj
    let level = 0

    while (current) {
      const props = Object.getOwnPropertyNames(current)

      for (const prop of props) {
        if (result[prop]) continue

        const desc = Object.getOwnPropertyDescriptor(current, prop)

        result[prop] = {
          from: level === 0 ? label : `__proto__ level ${level}`,
          descriptor: desc
            ? {
                configurable: desc.configurable,
                enumerable: desc.enumerable,
                writable: desc.writable,
                hasGetter: !!desc.get,
                hasSetter: !!desc.set
              }
            : null,
          value: safeGet(obj, prop)
        }
      }

      current = Object.getPrototypeOf(current)
      level++
    }

    return result
  }

  const data = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    languages: navigator.languages,
    webdriver: navigator.webdriver,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory,
    maxTouchPoints: navigator.maxTouchPoints,

    plugins: Array.from(navigator.plugins || []).map(p => ({
      name: p.name,
      filename: p.filename,
      description: p.description
    })),

    mimeTypes: Array.from(navigator.mimeTypes || []).map(m => ({
      type: m.type,
      suffixes: m.suffixes,
      description: m.description
    })),

    permissions: await (async () => {
      try {
        const names = ["geolocation", "notifications", "camera", "microphone"]
        const out = {}
        for (const name of names) {
          try {
            const res = await navigator.permissions.query({ name })
            out[name] = res.state
          } catch (e) {
            out[name] = "error"
          }
        }
        return out
      } catch {
        return "unsupported"
      }
    })(),

    navigatorDump: dumpObject(navigator, "navigator")
  }

  const json = JSON.stringify(data, null, 2)

  try {
    await navigator.clipboard.writeText(json)
    console.log("Snapshot copied to clipboard")
  } catch (e) {
    console.log("Clipboard failed → printing JSON below")
    console.log(json)
  }

  return data
})()