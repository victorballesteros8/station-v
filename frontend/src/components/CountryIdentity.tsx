interface CountryIdentityProps {
  iso2: string
  name: string
}

const COUNTRY_NAMES: Record<string, string> = {
  IN: "India",
  EG: "Egipto",
  PK: "Pakistán",
  JP: "Japón",
  UA: "Ucrania",
}

function CountryIdentity({
  iso2,
  name,
}: CountryIdentityProps) {
  const normalizedIso2 = iso2.toUpperCase()

  const displayName =
    COUNTRY_NAMES[normalizedIso2] ?? name

  return (
    <div className="country-identity">
      <span
        className="country-flag"
        aria-hidden="true"
      >
        {normalizedIso2
          .split("")
          .map(
            (letter) =>
              String.fromCodePoint(
                127397 + letter.charCodeAt(0),
              ),
          )
          .join("")}
      </span>

      <span className="country-name">
        {displayName}
      </span>
    </div>
  )
}

export default CountryIdentity