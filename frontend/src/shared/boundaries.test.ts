import { combinedBoundaries } from './boundaries'

describe('combinedBoundaries', () => {
  test('should return undefined for empty array', () => {
    // tslint:disable-next-line:no-unused-expression - bug in linter
    expect(combinedBoundaries([])).toBeUndefined
  })

  test('should return first element for singleton array', () => {
    const element = { left: 0, right: 123 }
    expect(combinedBoundaries([element])).toEqual(element)
  })

  test('should return combined boundaries for multiple items', () => {
    const items = [{ left: 20, right: 80 }, { left: 15, right: 75 }, { left: 15, right: 70 }]
    const expected = { left: 15, right: 80 }
    expect(combinedBoundaries(items)).toEqual(expected)
  })
})
