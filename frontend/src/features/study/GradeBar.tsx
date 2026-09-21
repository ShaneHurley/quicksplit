import { ClayButton } from '../../components/ui/ClayButton'

type Props = {
  disabled?: boolean
  onGrade: (grade: 1 | 2 | 3 | 4) => void
}

export function GradeBar({ disabled, onGrade }: Props) {
  return (
    <div className="mx-auto mt-8 grid max-w-xl grid-cols-2 gap-3 sm:grid-cols-4">
      <ClayButton tone="peach" disabled={disabled} type="button" onClick={() => onGrade(1)}>
        Again
      </ClayButton>
      <ClayButton tone="butter" disabled={disabled} type="button" onClick={() => onGrade(2)}>
        Hard
      </ClayButton>
      <ClayButton tone="mint" disabled={disabled} type="button" onClick={() => onGrade(3)}>
        Good
      </ClayButton>
      <ClayButton tone="sky" disabled={disabled} type="button" onClick={() => onGrade(4)}>
        Easy
      </ClayButton>
    </div>
  )
}
